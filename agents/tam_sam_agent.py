from state_types import DeckAnalysisState
from agents.topic_extract import get_relevant_pages


def tam_sam_agent(state: DeckAnalysisState) -> DeckAnalysisState:
    print("[Starting Tam Sam Agent]")

    # Get market size slides
    market_size_pages = get_relevant_pages(state, "market_size_slide")

    # Process market size content
    for page in market_size_pages:
        print(f"Processing market size page {page['page_number']}: {page['text'][:100]}...")
        # Add your market size analysis logic here

    return state


