from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.graph.message import add_messages


def deck_analysis_agent(pdf_url: str):
    
    #get dictionary of pdf pages and their text
    pdf_pages = get_pdf_pages(pdf_url)
    
    return StateGraph(
        START,
        END,
        add_messages,
    )