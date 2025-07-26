from state_types import DeckAnalysisState
from agents.topic_extract import get_relevant_pages
from utils.llm import query_pdf_page
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from utils.search_client import search_tavily
import json
from dotenv import load_dotenv

load_dotenv()
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)

def analyse_competition_agent(state: DeckAnalysisState) -> DeckAnalysisState:
    """
    Analyzes competitor claims in the pitch deck by verifying specific statements
    made about competitors rather than doing general market research.
    """
    print("[Starting Analyse Competition Agent - Claim Verification Mode]")
    
    # Check if there are any competitor slides to analyze
    competitor_pages = [topic for topic in state["topics"] if topic.get("topic") == "competitors_slide"]
    
    if competitor_pages:
        # Use the first competitor page found
        competitor_page = competitor_pages[0]
        page_index = competitor_page.get("page_number", 1) - 1
        pdf_path = "test_pitch_solea.pdf"
        
        print(f"Analyzing competitor claims on page {page_index}")
        
        # Step 1: Extract specific claims about competitors
        competitor_claims = extract_competitor_claims(page_index, pdf_path)
        
        # Step 2: Verify each claim individually
        verified_claims = verify_all_claims(competitor_claims)
        
        # Step 3: Generate final feedback based on claim accuracy
        final_feedback = generate_claim_verification_feedback(verified_claims, state["general_context"])
        
        # Store results
        state["page_feedback"] = {
            "competitor_claims": competitor_claims,
            "verified_claims": verified_claims,
            "accuracy_summary": calculate_overall_accuracy(verified_claims),
            "written_feedback": final_feedback,
            "verification_mode": "claim_fact_checking"
        }
    
    return state


def extract_competitor_claims(page_number: int, pdf_path: str) -> dict:
    """Extract specific, verifiable claims about competitors from the PDF page"""
    
    extraction_prompt = """
    Extract ALL specific claims about competitors from this slide. Focus on FACTUAL STATEMENTS that can be verified, not opinions.

    Return ONLY valid JSON in this exact format:
    {
      "competitor_claims": [
        {
          "competitor_name": "Exact company name mentioned",
          "factual_claims": [
            "They have X number of users",
            "They raised $X million in funding", 
            "They were founded in YEAR",
            "They operate in X countries"
          ],
          "feature_claims": [
            "They only support X feature",
            "They don't have Y capability",
            "Their platform is limited to Z"
          ],
          "performance_claims": [
            "They are slower than us",
            "They have higher prices",
            "They have poor customer satisfaction"
          ],
          "positioning_claims": [
            "We are better because...",
            "Unlike them, we...",
            "They target X market, we target Y"
          ]
        }
      ],
      "market_position_claims": [
        "We are the first to...",
        "No one else does...",
        "The market size is $X billion"
      ]
    }

    Extract EXACT wording used in the slide. If no competitors mentioned, return empty arrays.
    """
    
    raw_response = query_pdf_page(page_number, extraction_prompt, pdf_path)
    return parse_json_safely(raw_response)


def verify_all_claims(competitor_claims: dict) -> list:
    """Verify claims made about competitors using minimal searches"""
    
    all_verified_claims = []
    
    # Verify competitor-specific claims (1-2 searches per competitor)
    for competitor in competitor_claims.get("competitor_claims", []):
        competitor_name = competitor.get("competitor_name", "")
        print(f"Verifying claims about: {competitor_name}")
        
        # Collect all claims for this competitor
        all_claims = []
        all_claims.extend(competitor.get("factual_claims", []))
        all_claims.extend(competitor.get("feature_claims", []))
        all_claims.extend(competitor.get("performance_claims", []))
        all_claims.extend(competitor.get("positioning_claims", []))
        
        if all_claims:
            # Do 1-2 searches per competitor to verify ALL their claims
            verification_results = verify_competitor_batch(competitor_name, all_claims)
            
            # Add individual claim results
            for i, claim in enumerate(all_claims):
                all_verified_claims.append({
                    "competitor": competitor_name,
                    "claim": claim,
                    "claim_type": categorize_claim_type(claim, competitor),
                    "verification": verification_results[i] if i < len(verification_results) else {"verdict": "insufficient_evidence"}
                })
    
    # Verify market position claims (1 search for all market claims)
    market_claims = competitor_claims.get("market_position_claims", [])
    if market_claims:
        print(f"Verifying {len(market_claims)} market claims...")
        market_verification_results = verify_market_claims_batch(market_claims)
        
        for i, market_claim in enumerate(market_claims):
            all_verified_claims.append({
                "competitor": "MARKET_CLAIM",
                "claim": market_claim,
                "claim_type": "market_positioning",
                "verification": market_verification_results[i] if i < len(market_verification_results) else {"verdict": "insufficient_evidence"}
            })
    
    return all_verified_claims


def verify_competitor_batch(competitor_name: str, all_claims: list) -> list:
    """Verify all claims about a competitor using 1-2 searches total"""
    
    # General company info search
    general_query = f'"{competitor_name}" company business model features users funding'
    general_results = search_tavily(general_query, max_results=3)
    
    # Performance/comparison search if there are performance claims
    performance_claims = [c for c in all_claims if any(word in c.lower() for word in ["faster", "slower", "better", "price", "cost"])]
    performance_results = []
    if performance_claims:
        perf_query = f'"{competitor_name}" pricing performance reviews comparison'
        performance_results = search_tavily(perf_query, max_results=2)
    
    # Let LLM verify all claims at once using the search results
    verification_prompt = f"""
    Verify ALL these claims about {competitor_name} using the search results provided:
    
    CLAIMS TO VERIFY:
    {json.dumps(all_claims, indent=2)}
    
    GENERAL COMPANY INFO:
    {json.dumps(general_results, indent=2)}
    
    PERFORMANCE/COMPARISON INFO:
    {json.dumps(performance_results, indent=2)}
    
    For each claim, return verification in this JSON format:
    {{
      "claim_verifications": [
        {{
          "claim": "exact claim text",
          "verdict": "accurate|inaccurate|partially_accurate|insufficient_evidence",
          "confidence": "high|medium|low",
          "supporting_evidence": "Specific evidence",
          "contradicting_evidence": "Contradicting evidence if any",
          "accuracy_score": 75,
          "evidence_quality": "strong|moderate|weak|none"
        }}
      ]
    }}
    
    Verify each claim in the order provided. Be strict with accuracy.
    """
    
    response = llm.invoke([HumanMessage(content=verification_prompt)])
    result = parse_json_safely(response.content)
    
    return result.get("claim_verifications", [{"verdict": "insufficient_evidence"}] * len(all_claims))


def verify_market_claims_batch(market_claims: list) -> list:
    """Verify all market claims using one search"""
    
    # Combine all market claims into one search
    claims_text = " ".join(market_claims)
    search_query = f'{claims_text} market research statistics data'
    search_results = search_tavily(search_query, max_results=3)
    
    verification_prompt = f"""
    Verify ALL these market claims using the search results:
    
    MARKET CLAIMS TO VERIFY:
    {json.dumps(market_claims, indent=2)}
    
    SEARCH RESULTS:
    {json.dumps(search_results, indent=2)}
    
    For each claim, return verification in this JSON format:
    {{
      "claim_verifications": [
        {{
          "claim": "exact claim text",
          "verdict": "accurate|inaccurate|partially_accurate|insufficient_evidence",
          "confidence": "high|medium|low",
          "supporting_evidence": "Data/sources that support the claim",
          "contradicting_evidence": "Data that contradicts the claim",
          "accuracy_score": 75,
          "evidence_quality": "strong|moderate|weak|none"
        }}
      ]
    }}
    
    Verify each claim in the order provided.
    """
    
    response = llm.invoke([HumanMessage(content=verification_prompt)])
    result = parse_json_safely(response.content)
    
    return result.get("claim_verifications", [{"verdict": "insufficient_evidence"}] * len(market_claims))


def categorize_claim_type(claim: str, competitor: dict) -> str:
    """Categorize the type of claim being made"""
    
    claim_lower = claim.lower()
    
    if any(word in claim_lower for word in ["users", "customers", "revenue", "funding", "founded", "employees"]):
        return "factual_business_data"
    elif any(word in claim_lower for word in ["feature", "capability", "support", "platform", "technology"]):
        return "feature_comparison"
    elif any(word in claim_lower for word in ["price", "cost", "expensive", "cheap", "faster", "slower"]):
        return "performance_comparison"
    elif any(word in claim_lower for word in ["better", "unlike", "different", "superior", "advantage"]):
        return "positioning_claim"
    else:
        return "general_claim"


def calculate_overall_accuracy(verified_claims: list) -> dict:
    """Calculate overall accuracy metrics"""
    
    if not verified_claims:
        return {"overall_accuracy": 0, "total_claims": 0}
    
    total_claims = len(verified_claims)
    accurate_count = 0
    partially_accurate_count = 0
    inaccurate_count = 0
    insufficient_evidence_count = 0
    
    total_accuracy_score = 0
    
    for claim_result in verified_claims:
        verification = claim_result.get("verification", {})
        verdict = verification.get("verdict", "insufficient_evidence")
        accuracy_score = verification.get("accuracy_score", 0)
        
        total_accuracy_score += accuracy_score
        
        if verdict == "accurate":
            accurate_count += 1
        elif verdict == "partially_accurate":
            partially_accurate_count += 1
        elif verdict == "inaccurate":
            inaccurate_count += 1
        else:
            insufficient_evidence_count += 1
    
    return {
        "total_claims": total_claims,
        "accurate_claims": accurate_count,
        "partially_accurate_claims": partially_accurate_count,
        "inaccurate_claims": inaccurate_count,
        "insufficient_evidence_claims": insufficient_evidence_count,
        "average_accuracy_score": round(total_accuracy_score / total_claims, 1) if total_claims > 0 else 0,
        "credibility_rating": get_credibility_rating(accurate_count, partially_accurate_count, inaccurate_count, total_claims)
    }


def get_credibility_rating(accurate: int, partial: int, inaccurate: int, total: int) -> str:
    """Determine overall credibility rating"""
    
    if total == 0:
        return "unknown"
    
    accuracy_percentage = (accurate + partial * 0.5) / total * 100
    
    if accuracy_percentage >= 80:
        return "high_credibility"
    elif accuracy_percentage >= 60:
        return "moderate_credibility"
    elif accuracy_percentage >= 40:
        return "low_credibility"
    else:
        return "very_low_credibility"


def generate_claim_verification_feedback(verified_claims: list, general_context: str) -> str:
    """Generate final feedback based on claim verification results"""
    
    accuracy_summary = calculate_overall_accuracy(verified_claims)
    
    feedback_prompt = f"""
    Write CONCISE feedback on the accuracy of competitor claims in this pitch deck.
    
    CLAIM VERIFICATION RESULTS:
    {json.dumps(verified_claims, indent=2)}
    
    ACCURACY SUMMARY:
    {json.dumps(accuracy_summary, indent=2)}
    
    STARTUP CONTEXT:
    {general_context}
    
    Write feedback focusing on:
    1. Which specific claims are ACCURATE vs INACCURATE (be specific)
    2. Any misleading or unfair characterizations of competitors
    3. Overall credibility of their competitive analysis
    4. Red flags or concerning inaccuracies
    
    Be direct and factual. Include specific examples of inaccurate claims.
    Embed source URLs in markdown format where available.
    Keep it under 200 words but be impactful.
    """
    
    response = llm.invoke([HumanMessage(content=feedback_prompt)])
    return response.content


def parse_json_safely(text: str) -> dict:
    """Safely parse JSON from LLM response with error handling"""
    
    try:
        # Clean up the text
        text = text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        # Parse JSON
        return json.loads(text)
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {e}")
        print(f"Raw text: {text[:200]}...")
        
        # Try to extract JSON object from text
        try:
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_text = text[start_idx:end_idx]
                return json.loads(json_text)
        except:
            pass
        
        # Return error structure
        return {
            "error": "Failed to parse JSON response",
            "raw_text": text[:500],
            "competitor_claims": [],
            "market_position_claims": []
        }