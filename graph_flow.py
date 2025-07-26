from langgraph.graph import StateGraph
from typing import TypedDict, List, Dict, Any, Optional
from agents.tam_sam_agent import tam_sam_agent
from agents.topic_extract import topic_extractor_agent
from dotenv import load_dotenv
from state_types import DeckAnalysisState
from langgraph.constants import START, END

load_dotenv()


def run_vc_analysis(page_content: List[Dict[str, Any]], whole_text: str) -> DeckAnalysisState:
    initial_state = {
        "page_content": page_content,
        "whole_text": whole_text,
        "page_feedback": [],
        "topic_feedback": [],
    }





    flow = StateGraph(DeckAnalysisState)

    flow.add_node("topic_extractor_agent", topic_extractor_agent)
    flow.add_node("tam_sam_agent", tam_sam_agent)

    flow.add_edge(START, "topic_extractor_agent")
    flow.add_edge("topic_extractor_agent", "tam_sam_agent")
    flow.add_edge("tam_sam_agent", END)

    built_flow = flow.compile()
    final_state = built_flow.invoke(initial_state)

    png_data = built_flow.get_graph().draw_mermaid_png()
    with open("agent_graph.png", "wb") as f:
        f.write(png_data)
    return final_state






