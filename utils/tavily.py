from tavily import TavilyClient
from utils.config import TAVILY_API_KEY


tavily_client = TavilyClient(api_key="tvly-TAVILY_API_KEY")

def search_tavily(query):
    response = tavily_client.search(query)
    return response

