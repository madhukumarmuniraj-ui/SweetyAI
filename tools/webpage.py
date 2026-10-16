import requests


SEARXNG_URL = "http://localhost:8080/search"


def web_search(query: str):

    print(
        f"\n[SYSTEM]: Searching the web for '{query}'..."
    )

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

        for result in results[:5]:

            title = result.get(
                "title",
                "No title"
            )

            snippet = result.get(
                "content",
                "No snippet"
            )

            link = result.get(
                "url",
                ""
            )

            output.append(
                f"Title: {title}\n"
                f"Snippet: {snippet}\n"
                f"Link: {link}"
            )

        return "\n\n".join(output)

    except Exception as error:

        return f"Search error: {error}"import requests


SEARXNG_URL = "http://localhost:8080/search"


def web_search(query: str):

    print(
        f"\n[SYSTEM]: Searching the web for '{query}'..."
    )

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

        for result in results[:5]:

            title = result.get(
                "title",
                "No title"
            )

            snippet = result.get(
                "content",
                "No snippet"
            )

            link = result.get(
                "url",
                ""
            )

            output.append(
                f"Title: {title}\n"
                f"Snippet: {snippet}\n"
                f"Link: {link}"
            )

        return "\n\n".join(output)

    except Exception as error:

        return f"Search error: {error}"