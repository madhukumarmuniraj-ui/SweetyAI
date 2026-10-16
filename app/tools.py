import os
import datetime
import subprocess
import glob
import requests
import pyperclip
from app.doc_generator import generate_legal_document

def get_current_time():
    """Returns the current date and time."""
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S (%A)")

def open_workspace_folder():
    """Opens the current workspace folder in the file explorer."""
    try:
        path = os.getcwd()
        if os.name == 'nt':
            os.startfile(path)
        elif os.name == 'posix':
            subprocess.Popen(['xdg-open', path])
        return f"Opened workspace folder: {path}"
    except Exception as e:
        return f"Failed to open folder: {str(e)}"

def list_knowledge_documents():
    """Lists all documents indexed in the local knowledge base."""
    upload_dir = "./knowledge_base_docs"
    if not os.path.exists(upload_dir):
        return "No knowledge documents directory found."
    files = os.listdir(upload_dir)
    if not files:
        return "The knowledge base directory is empty."
    return "Indexed documents:\n- " + "\n- ".join(files)

def search_local_files(query: str):
    """Searches for local files matching the query."""
    upload_dir = "./knowledge_base_docs"
    if not os.path.exists(upload_dir):
        return "No knowledge documents directory found."
    matches = glob.glob(os.path.join(upload_dir, f"*{query}*"))
    if not matches:
        return f"No local files found matching '{query}'."
    return "Matching files:\n- " + "\n- ".join([os.path.basename(m) for m in matches])

def search_searxng(query: str):
    """Performs a web search via local SearXNG instance."""
    searxng_url = "http://localhost:8080/search"
    params = {"q": query, "format": "json"}
    try:
        response = requests.get(searxng_url, params=params, timeout=5)
        if response.status_code == 200:
            results = response.json().get("results", [])
            if not results:
                return "No web results found."
            snippets = []
            for r in results[:3]:
                snippets.append(f"- [{r.get('title')}]({r.get('url')}): {r.get('content')}")
            return "\n".join(snippets)
        else:
            return f"SearXNG returned status code {response.status_code}"
    except Exception as e:
        return f"Web search error (SearXNG might be offline): {str(e)}"

def read_clipboard_text():
    """Reads the current text from the system clipboard."""
    try:
        text = pyperclip.paste()
        if not text.strip():
            return "The clipboard is currently empty."
        return text
    except Exception as e:
        return f"Failed to read clipboard: {str(e)}"

# Complete registry of all available tools
AVAILABLE_TOOLS = {
    "get_current_time": get_current_time,
    "open_workspace_folder": open_workspace_folder,
    "list_knowledge_documents": list_knowledge_documents,
    "search_local_files": search_local_files,
    "search_searxng": search_searxng,
    "read_clipboard_text": read_clipboard_text,
    "generate_legal_document": generate_legal_document
}