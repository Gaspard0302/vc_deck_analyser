from state_types import DeckAnalysisState
from dotenv import load_dotenv
import os
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
import json

load_dotenv()

llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)

# create a final summary agent that will take the state and give a final summary of what was false or misleading

def final_summary_agent(state: DeckAnalysisState) -> DeckAnalysisState:
    print("[Starting Final Summary Agent]")

    # get the page feedback
    page_feedback = state.get("page_feedback", {})

    # get the tam sam info
    tam_sam_info = state.get("tam_sam_info", "")

    # get the tam sam sources
    tam_sam_sources = state.get("tam_sam_sources", [])

    # get the page content
    page_content = state.get("page_content", [])

    # get the topics
    topics = state.get("topics", [])

    # Check if we have both team and market size slides
    has_team_slide = any(t.get("topic") == "team_slide" for t in topics)
    has_market_slide = any(t.get("topic") == "market_size_slide" for t in topics)

    if has_team_slide or has_market_slide:
        # Get the relevant page numbers
        team_page = next((t for t in topics if t.get("topic") == "team_slide"), None)
        market_page = next((t for t in topics if t.get("topic") == "market_size_slide"), None)

        # Get the page content for the relevant pages
        relevant_pages = []
        if team_page:
            relevant_pages.append({
                "page_number": team_page["page_number"],
                "content": next((p for p in page_content if p["page_number"] == team_page["page_number"] - 1), {}),
                "feedback": page_feedback.get("written_feedback", ""),
                "type": "team"
            })

        if market_page:
            relevant_pages.append({
                "page_number": market_page["page_number"],
                "content": next((p for p in page_content if p["page_number"] == market_page["page_number"] - 1), {}),
                "feedback": tam_sam_info,
                "type": "market"
            })

        system_message = SystemMessage(content="""
        You are an expert synthesiser. You will be given information about negative feedback on a pitch deck.
        For a given slide, you will be given information about the coordinates "text_with_coordinates" of where on the slide the feedback is related to.
        It is your job to match the feedback to the correct coordinates on the slide.
        You must return a list of dictionaries with the following keys:
        [
            {
                "feedback": "specific feedback about this element",
                "coordinates": {"x0": 100, "y0": 200, "x1": 300, "y1": 250},
                "page_number": 1,
                "slide_type": "team_slide or market_size_slide",
                "status": "refuted or unclear"
            }
        ]

        IMPORTANT: Each feedback item must include the exact page_number so the frontend knows which page to display the feedback on.
        The "status" field should be:
        - "refuted" if the information has been clearly disproven or contradicted
        - "unclear" if the information cannot be verified or is ambiguous
        Match the feedback to the most relevant text blocks on the slide based on the coordinates provided.
        """)

        human_message = HumanMessage(content=f"""
        Here is the feedback and page information:

        Team slide feedback: {page_feedback.get('written_feedback', 'No team feedback')}
        Market size feedback: {tam_sam_info}

        Relevant pages with coordinates: {json.dumps(relevant_pages, indent=2)}

        For each feedback item, make sure to include the correct page_number that corresponds to the slide being analyzed.
        """)

        messages = [system_message, human_message]
        response = llm.invoke(messages)

        # Parse the response and add to state
        try:
            # Ensure we get a string from the response
            response_text = str(response.content)
            matched_feedback = json.loads(response_text)
            state["matched_feedback"] = matched_feedback
            print(f"Matched feedback: {matched_feedback}")
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {response.content}")
            print(f"JSON error: {e}")
            state["matched_feedback"] = []
        except Exception as e:
            print(f"Unexpected error parsing response: {e}")
            state["matched_feedback"] = []

    print(state["matched_feedback"])

    return state


