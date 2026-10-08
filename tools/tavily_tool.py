from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()


def tavily_search(query):
    # Create the client on each call so the latest TAVILY_API_KEY from secrets is used
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Hotel search is unavailable right now (TAVILY_API_KEY is not set)."

    try:
        response = TavilyClient(api_key=api_key).search(
            query=query,
            max_results=5
        )
    except Exception:
        # Network errors or API outages should not crash the whole travel plan
        return "Hotel search is unavailable right now. Please try again in a minute."

    results = []

    for i, r in enumerate(response.get("results", []), 1):
        title = r.get("title", "Unknown")
        url = r.get("url", "")
        snippet = r.get("content", "").strip()
        # Keep only the first 300 characters to avoid long snippets
        if len(snippet) > 300:
            snippet = snippet[:300].rsplit(" ", 1)[0] + "..."

        results.append(f"{i}. **{title}**\n {url}\n {snippet}\n")

    return "\n".join(results) if results else "No hotel results found."
