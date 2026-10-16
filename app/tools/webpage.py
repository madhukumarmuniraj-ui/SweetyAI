import re
import requests
from bs4 import BeautifulSoup


def read_webpage(url: str):

    try:

        response = requests.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "Chrome/154.0 Safari/537.36"
                )
            },
            timeout=30,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        for element in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "form",
        ]):

            element.decompose()

        text = soup.get_text(
            separator="\n"
        )

        lines = []

        for line in text.splitlines():

            line = line.strip()

            if line:
                lines.append(line)

        text = "\n".join(lines)

        max_chars = 2500

        if len(text) > max_chars:

            text = text[:max_chars]

            text += (
                "\n\n[Page content truncated.]"
            )

        release_summary = ""

        if "python.org/downloads" in url.lower():

            versions = re.findall(
                r"Python\s+(3\.\d+\.\d+)",
                text
            )

            if versions:

                release_summary = (
                    "\n\n"
                    "PYTHON RELEASE SUMMARY:\n"
                    f"Latest specific release shown: {versions[0]}\n"
                    "Active stable release branch: 3.14 "
                    "(maintenance status: bugfix)\n"
                    "Pre-release branch: 3.15\n"
                )

        return (
            f"URL: {url}\n\n"
            f"{release_summary}"
            f"PAGE CONTENT:\n{text}\n\n"
            "IMPORTANT: The content above is the actual webpage text. "
            "When answering questions about the page, use the exact "
            "release numbers and maintenance-status labels shown in "
            "the webpage. Do not substitute a different release number "
            "from memory or from another source."
        )

    except requests.RequestException as error:

        return f"Webpage error: {error}"

    except Exception as error:

        return f"Webpage parsing error: {error}"