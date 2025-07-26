from typing import TypedDict, List, Dict, Any


class DeckAnalysisState(TypedDict):
    page_content: List[Dict[str, Any]] # input (should not be modified by agents)
    whole_text: str # input (should not be modified by agents)
    page_feedback: List[Dict[str, Any]] # output
    topics: List[Dict[str, Any]] # output




