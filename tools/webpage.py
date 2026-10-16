"""SweetyAI Web Search Tool (SearXNG backed).

Searches via a local SearXNG instance (default http://localhost:8080) and
returns a formatted digest of the top results.
"""

import requests

SEARXNG_URL = "http://localhost:8080/search"
MAX_RESULTS = 5


def web_search(query: str) -> str:
    """Search the web using the local SearXNG instance.

    Returns a formatted string of the top results, or a human-readable
    error message if the search instance is unreachable.
    """
    print(f"\n[SYSTEM]: Searching the web for '{query}'...")

    try:
        response = requests.get(
            SEARXNG_URL,
            params={
                "q": query,
                "format": "json",
            },
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("results", [])

        if not results:
            return "No results found."

        output = []

        for result in results[:MAX_RESULTS]:
            title = result.get("title", "No title")
            snippet = result.get("content", "No snippet")
            link = result.get("url", "")

            output.append(
                f"Title: {title}\n"
                f"Snippet: {snippet}\n"
                f"Link: {link}"
            )

        return "\n\n".join(output)

    except Exception as error:
        return f"Search error: {error}"


def read_webpage(url: str) -> str:
    """Fetch a web page URL and return its raw text content (best effort)."""
    try:
        response = requests.get(url, timeout=15, headers={"User-Agent": "SweetyAI/1.0"})
        response.raise_for_status()
        return response.text
    except Exception as error:
        return f"Webpage fetch error: {error}"


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        print(web_search(" ".join(sys.argv[1:])))
    else:
        print("Usage: python3 tools/webpage.py <search query>")
