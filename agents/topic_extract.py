from state_types import DeckAnalysisState
from dotenv import load_dotenv
import os
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)

def topic_extractor_agent(state: DeckAnalysisState) -> DeckAnalysisState:
    print("[Starting Topic Extractor Agent]")

    page_content = state["page_content"]
    topics = []

    for page in page_content:
        page_text = page["text"]
        page_number = page.get("page_number", None)

        system_message = SystemMessage(content="""
        You are a helpful assistant for a venture capitalist firm that extracts topics from a given text of a slide.
        You will be given the raw text of a single slide and you need to extract the topic from the text.
        The list of possible topics that you can choose from are:
        - "market_size_slide"
        - "team_slide"
        - "competitors_slide"
        - "problem_slide"
        - "solution_slide"
        - "fundraising_slide"
        - "business_model_slide"
        - "other"

        If the topic does not fit any main topics, you must return "other" and only "other".
        You must ONLY return the topic for this page as one of the topics in the list ONLY.
        """)

        human_message = HumanMessage(content=f"Here is the raw text of the slide: {page_text}")
        messages = [system_message, human_message]
        response = llm.invoke(messages)

        topics.append({
            "page_number": page_number+1,
            "topic": response.content.strip()
        })

    state["topics"] = topics
    print(state["topics"])
    return state
