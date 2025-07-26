from state_types import DeckAnalysisState
from dotenv import load_dotenv
import os
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from utils.llm import query_pdf_page
from utils.search_client import search_tavily
import json



import pprint


load_dotenv()

llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)


def founders_background_agent(state: DeckAnalysisState) -> DeckAnalysisState:
    print("[Starting Founders Backround Agent]")

    team_pages = [t for t in state["topics"] if t.get("topic") == "team_slide"]
    if not team_pages:
        return state
    # Use the first team slide (as per your new logic)
    page = team_pages[0]

    page_content = page["page_text"]
    page_number = page["page_number"]-1
    pdf_path = "test_pitch_solea.pdf"

    print(page_number)

    # Extract structured founder info
    extraction_prompt = """Extract founders information and return ONLY valid JSON, Make sure information is correct and that there are no duplicates:

{
  "founders": [
    {
      "name": "Full Name",
      "role": "CEO/CTO/Founder/etc",
      "background": "Previous companies and roles",
      "experience": "Years of experience or key achievements",
      "education": "University, degree, graduation year",
      "skills": "Technical skills, programming languages, expertise areas",
      "interests": "Relevant interests or specializations"
    }
  ]
}

If no founders found, return: {"founders": []}
"""

    founders_raw = query_pdf_page(page_number, extraction_prompt, pdf_path)
    founders_info = parse_json_response(founders_raw)

    # Verify each founder
    verified_founders = []
    for founder in founders_info.get("founders", []):
        print(f"Verifying {founder.get('name', 'Unknown')}")
        internet_founder_backround = search_founder_background(founder)

        # Get verification analysis
        analysis = analyze_founder_verification(founder, internet_founder_backround)

        verified_founders.append({
            **founder,
            "internet_verification": internet_founder_backround,
            "credibility_analysis": analysis
        })

    final_feedback_prompt = f"""
    Here is the feedback for the founders: {verified_founders} that is checked against the internet.
    Write a SHORT and CONCISE feedback for the founders.
    Imbedd the source of the feedback in the feedback.
    All the information comes from a pitch deck for their startup. Here is the context {state["general_context"]}
    Say if the founders are credible and if the information is correct and if they are correct team for this project (i.e might be missing a technical founder)
    """

    final_feedback = llm.invoke([HumanMessage(content=final_feedback_prompt)])
    final_feedback = final_feedback.content

    state["page_feedback"] = {
        "verified_founders": verified_founders,
        "total_founders": len(verified_founders),
        "written_feedback": final_feedback
    }
    print(state["page_feedback"])

    return state


def search_founder_background(founder: dict) -> dict:
    """Search for founder information online"""
    name = founder.get("name", "")
    if not name:
        return {"error": "No name provided"}

    # LinkedIn search
    linkedin_query = f"{name} LinkedIn profile, past jobs, education, skills, interests"
    linkedin_results = search_tavily(linkedin_query, max_results=2)

    # Startup experience search
    startup_query = f"{name} startup founder CEO CTO entrepreneur"
    startup_results = search_tavily(startup_query, max_results=1)

    return {
        "linkedin_search": linkedin_results,
        "startup_search": startup_results,
        "search_success": bool(linkedin_results or startup_results)
    }



def analyze_founder_verification(founder: dict, internet_founder_backround: dict) -> dict:
    """Analyze founder claims against internet findings"""

    analysis_prompt = f"""
Analyze this founder's claimed background against internet search results.

FOUNDER CLAIMS:
{json.dumps(founder, indent=2)}

INTERNET SEARCH RESULTS:
{json.dumps(internet_founder_backround, indent=2)}

Return ONLY valid JSON with this structure:
{{
  "credibility_score": 85,
  "is_technical_founder": true,
  "background_verified": true,
  "linkedin_found": true,
  "startup_experience": true,
  "discrepancies": ["Any inconsistencies found"],
  "technical_evidence": ["Programming languages", "Engineering roles", "CS degree"],
  "verified_facts": ["Confirmed previous roles", "Education verified"],
  "red_flags": ["Any concerning findings"],
  "confidence_level": "high"
}}

Score from 0-100. Confidence: low/medium/high.
"""

    response = llm.invoke([HumanMessage(content=analysis_prompt)])
    response_text = str(response.content)

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        print(f"Failed to parse analysis JSON: {response_text[:200]}...")
        return {
            "credibility_score": 0,
            "is_technical_founder": False,
            "background_verified": False,
            "linkedin_found": False,
            "startup_experience": False,
            "discrepancies": ["Failed to parse analysis"],
            "technical_evidence": [],
            "verified_facts": [],
            "red_flags": ["Analysis parsing failed"],
            "confidence_level": "low"
        }


def parse_json_response(text: str) -> dict:
    """Safely parse JSON from LLM response"""

    try:
        # Clean up common formatting issues
        text = text.strip()

        # Remove markdown code blocks
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        # Try to parse
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {e}")
        print(f"Text: {text[:200]}...")

        # Fallback: try to extract JSON from text
        try:
            # Find first { and last }
            start = text.find('{')
            end = text.rfind('}') + 1

            if start != -1 and end > start:
                json_text = text[start:end]
                return json.loads(json_text)

        except:
            pass

        # Return error dict if all fails
        return {
            "error": "Failed to parse JSON",
            "raw_response": text[:500]
        }




