from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query: str) -> dict:
    """
    Search the web using Tavily and return results.
    Returns a dict with results and sources.
    """
    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=5,
        include_answer=True
    )
    
    # Extract clean results
    results = []
    sources = []
    
    for result in response.get("results", []):
        results.append({
            "title": result.get("title", ""),
            "content": result.get("content", ""),
            "url": result.get("url", "")
        })
        sources.append(result.get("url", ""))
    
    return {
        "results": results,
        "sources": sources,
        "answer": response.get("answer", "")
    }