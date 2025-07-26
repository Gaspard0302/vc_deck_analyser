from state_types import DeckAnalysisState
from agents.topic_extract import get_relevant_pages
from utils.llm import query_pdf_page


def tam_sam_agent(state: DeckAnalysisState) -> DeckAnalysisState:
    print("[Starting Tam Sam Agent]")

    # Get market size slides (only use the first relevant slide if any)
    market_size_pages = get_relevant_pages(state, "market_size_slide")
    if market_size_pages:
        page = market_size_pages[0]


        # call the vlm to get the tam sam info
        prompt = f"""
        You are a helpful assistant that can extract the Tam Sam information from a given slide.
        Here is the slide:
        {page["text"]}
        """
        response = query_pdf_page(page["page_number"], prompt, "test_pitch_solea.pdf")


        state["tam_sam_info"] = response












    return state


