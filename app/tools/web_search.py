import urllib.request
import urllib.parse
import json
import re

def web_search(query: str) -> str:
    """Perform a live web search for the given query using a public endpoint."""
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
        snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html_content, re.DOTALL)
        
        cleaned_results = []
        for i in range(min(5, len(snippets))):
            clean_snippet = re.sub(r'<.*?>', '', snippets[i]).strip()
            cleaned_results.append(f"- {clean_snippet}")
            
        if cleaned_results:
            return f"Web Search Results for '{query}':\n" + "\n".join(cleaned_results)
        else:
            return f"No live search results found for '{query}'- try rephrasing."
            
    except Exception as e:
        return f"Search error: {str(e)}"
