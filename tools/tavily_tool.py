from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

# Limit results to hotel booking and review sites so the agent gets real hotels,
# not tour packages or social media posts
HOTEL_SITES = [
    "booking.com",
    "tripadvisor.com",
    "tripadvisor.in",
    "agoda.com",
    "makemytrip.com",
    "goibibo.com",
    "hotels.com",
    "expedia.co.in",
]

def tavily_search(query):
    # Create the client on each call so the latest TAVILY_API_KEY from secrets is used
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Hotel search is unavailable right now (TAVILY_API_KEY is not set)."

    try:
        response = TavilyClient(api_key=api_key).search(
            query=query,
            max_results=5,
            include_domains=HOTEL_SITES,
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
