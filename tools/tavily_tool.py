from tavily import TavilyClient
import os
import re
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

def _clean(text):
    """Strip markdown symbols and extra whitespace from web page text so it renders as plain text."""
    text = re.sub(r"[#*_>`|]+", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


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
        title = _clean(r.get("title", "Unknown"))
        url = r.get("url", "")
        snippet = _clean(r.get("content", ""))
        # Drop the page title if the snippet just repeats it
        if snippet.lower().startswith("title:"):
            snippet = snippet.split(" ", 1)[-1]
        # Keep only the first 250 characters to avoid long snippets
        if len(snippet) > 250:
            snippet = snippet[:250].rsplit(" ", 1)[0] + "..."

        results.append(f"{i}. **{title}**  \n{snippet} [View]({url})")

    return "\n\n".join(results) if results else "No hotel results found."
