import os
import requests

GOOGLE_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
SEARCH_ENGINE_ID = os.getenv("GOOGLE_CSE_ID")

def google_search(query: str) -> str:
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query,
        "num": 3  # number of results
    }
    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        results = res.json().get("items", [])
        output = ""
        for i, item in enumerate(results):
            output += f"{i+1}. {item.get('title')}\n{item.get('snippet')}\n{item.get('link')}\n\n"
        return output.strip() if output else "No results found."
    except Exception as e:
        return f"Search failed: {e}"
