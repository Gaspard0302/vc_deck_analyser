from state_types import DeckAnalysisState
from agents.topic_extract import get_relevant_pages
from utils.llm import query_pdf_page
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_tavily import TavilySearch
from typing import List, Dict, Any

load_dotenv()

llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)
tavily = TavilySearch()  # Initialize Tavily

def tam_sam_agent(state: DeckAnalysisState) -> DeckAnalysisState:
    print("[Starting Tam Sam Agent]")

    general_context = state["general_context"]

    # Get market size slides (only use the first relevant slide if any)
    market_size_pages = get_relevant_pages(state, "market_size_slide")
    if not market_size_pages:
        return state  # No relevant slide found

    page = market_size_pages[0]

    # Extract TAM/SAM data from the slide
    prompt = f"""
    You are a helpful assistant that can extract the TAM/SAM information from a given slide.
    Here is the slide content:
    {page["text"]}
    """
    response = query_pdf_page(page["page_number"], prompt, "test_pitch_solea.pdf")

    # --- New Tavily integration ---
    print("[Running Tavily Search for market size validation...]")
    tavily_query = f"market size {page['text'][:200]} industry statistics"
    search_results = tavily.invoke(tavily_query)
    sources = [r['url'] for r in search_results['results']] if 'results' in search_results else []

    # --- Use LLM to fact-check ---
    system_message = SystemMessage(content="""
    You are a critical VC analyst that will be given information about the market size of a company.
    Your job is to fact check the information, comparing what is on the slide with the information from a web search and your knowledge.
    Look out for anything incorrect or misleading and also exaggerations, and cite the sources you found.
    You must be binary in your response, either the information is pretty much correct or it is a big exaggeration.
    If you can't find information, give your best estimate using first principles and compare to the information on the slide.
    """)

    human_message = HumanMessage(content=f"""
    General context: {general_context}
    Slide text: {page['text']}
    Extracted TAM/SAM: {response}
    Tavily sources: {sources}
    """)

    messages = [system_message, human_message]
    llm_response = llm.invoke(messages)

    # Save to state
    state["tam_sam_info"] = str(llm_response.content)
    state["tam_sam_sources"] = sources

    print(state["tam_sam_info"])
    print(state["tam_sam_sources"])

    return state
