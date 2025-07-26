from typing import TypedDict, List, Dict, Any


class DeckAnalysisState(TypedDict):
    general_context: str # input
    page_content: List[Dict[str, Any]] # input (should not be modified by agents)
    whole_text: str # input (should not be modified by agents)
    page_feedback: List[Dict[str, Any]] # output
    topics: List[Dict[str, Any]] # output
    tam_sam_info: str # output
    tam_sam_sources: List[str] # output
    matched_feedback: List[Dict[str, Any]] # output




