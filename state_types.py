from typing import TypedDict, List, Dict, Any


class DeckAnalysisState(TypedDict):
    page_content: List[Dict[str, Any]] # input
    whole_text: str # input
    page_feedback: List[Dict[str, Any]] # output
    topics: List[str] # output




