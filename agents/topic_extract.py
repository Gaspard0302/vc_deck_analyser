from state_types import DeckAnalysisState
from dotenv import load_dotenv
import os

load_dotenv()



def topic_extractor_agent(state: DeckAnalysisState) -> DeckAnalysisState:
    print("[Starting Topic Extractor Agent]")

    



    #extract topics from the whole text
    topics = extract_topics(state["whole_text"])

    #add topics to the state
    state["topics"] = topics


    return state
