from tavily import TavilyClient

try:
    from utils.config import TAVILY_API_KEY
except ImportError:
    from config import TAVILY_API_KEY


tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

def search_tavily(query, max_results=2):
    """Search using Tavily API
    Args:
        query: str - The search query
    Returns:
        dict - The search response from Tavily
    """
    response = tavily_client.search(query, max_results=max_results)
    return response

if __name__ == "__main__":
    print(search_tavily("What is the capital of France?")) 