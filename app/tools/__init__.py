import datetime
import os
import glob
import requests
from app.doc_generator import generate_legal_document
from .calculator import calculator
from .filesystem import list_files, read_file
from .file_manager import append_file, delete_file
from .search_project import search_project
from .web_search import web_search
from .webpage import read_webpage
from .write_file import write_file
from .clipboard import read_clipboard_text, write_clipboard_text
from .desktop_automation import open_application, get_system_info

# Advanced Tools
# from . import computer_control
from . import browser_automation
from . import document_processing
from . import image_processing
from . import media_processing
from . import email_calendar
from . import database_connectors
from . import api_ecosystem

def get_current_time() -> str:
    """Returns the current date and time on the local machine."""
    now = datetime.datetime.now()
    return now.strftime("%A, %B %d, %Y, %I:%M %p")

def open_workspace_folder() -> str:
    """Opens the local knowledge base documents folder in Windows Explorer."""
    folder_path = os.path.abspath("./knowledge_base_docs")
    os.makedirs(folder_path, exist_ok=True)
    try:
        if os.name == 'nt':
            os.startfile(folder_path)
        else:
            os.system(f'xdg-open "{folder_path}"')
        return "Opened the local workspace folder successfully."
    except Exception as e:
        return f"Could not open folder: {str(e)}"

def list_knowledge_documents() -> str:
    """Lists all files currently indexed in the local RAG knowledge base."""
    folder_path = "./knowledge_base_docs"
    if not os.path.exists(folder_path):
        return "No knowledge base directory found."
    files = os.listdir(folder_path)
    if not files:
        return "The knowledge base is currently empty."
    return "Indexed documents:\n- " + "\n- ".join(files)

def search_local_files(query: str) -> str:
    """Searches the knowledge base folder for files matching a specific keyword or extension."""
    folder_path = "./knowledge_base_docs"
    if not os.path.exists(folder_path):
        return "Knowledge base directory does not exist."

    search_pattern = os.path.join(folder_path, f"*{query}*")
    matches = glob.glob(search_pattern)

    if not matches:
        all_files = os.listdir(folder_path)
        filtered = [f for f in all_files if query.lower() in f.lower()]
        if filtered:
            return f"Found matching files in workspace: {', '.join(filtered)}"
        return f"No local files found matching '{query}'."

    file_names = [os.path.basename(m) for m in matches]
    return f"Found matching files: {', '.join(file_names)}"

def search_searxng(query: str) -> str:
    """Searches via local SearXNG instance or falls back to web search."""
    searxng_url = "http://localhost:8080/search"
    params = {"q": query, "format": "json"}
    try:
        response = requests.get(searxng_url, params=params, timeout=4)
        if response.status_code == 200:
            results = response.json().get("results", [])
            if not results:
                return "No web results found."
            snippets = []
            for r in results[:3]:
                snippets.append(f"- [{r.get('title')}]({r.get('url')}): {r.get('content')}")
            return "\n".join(snippets)
    except Exception:
        pass
    return web_search(query)

# Central Registry mapping all core and utility tools for SweetyAI
AVAILABLE_TOOLS = {
    # Core Tools
    "calculator": calculator,
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "append_file": append_file,
    "delete_file": delete_file,
    "search_project": search_project,
    "web_search": web_search,
    "search_searxng": search_searxng,
    "read_webpage": read_webpage,
    "get_current_time": get_current_time,
    "open_workspace_folder": open_workspace_folder,
    "list_knowledge_documents": list_knowledge_documents,
    "search_local_files": search_local_files,
    "read_clipboard_text": read_clipboard_text,
    "write_clipboard_text": write_clipboard_text,
    "generate_legal_document": generate_legal_document,
    "open_application": open_application,
    "get_system_info": get_system_info,

    # Computer Control
# # "move_mouse": computer_control.move_mouse,
# "click_mouse": computer_control.click_mouse,
# # "type_text": computer_control.type_text,
# "press_key": computer_control.press_key,
# "press_hotkey": computer_control.press_hotkey,
# "list_windows": computer_control.list_windows,
# "activate_window": computer_control.activate_window,
# "screenshot_region": computer_control.screenshot_region,

    # Browser Automation
    "browser_navigate": browser_automation.navigate_to_url,
    "browser_click": browser_automation.click_element,
    "browser_fill_form": browser_automation.fill_form_field,
    "browser_screenshot": browser_automation.take_screenshot,
    "browser_extract_text": browser_automation.extract_text,

    # Document Processing
    "read_docx": document_processing.read_docx,
    "write_docx": document_processing.write_docx,
    "read_excel": document_processing.read_excel,
    "write_excel": document_processing.write_excel,
    "ocr_image": document_processing.ocr_image,
    "extract_pdf_text": document_processing.extract_pdf_text,

    # Image Processing
    "resize_image": image_processing.resize_image,
    "crop_image": image_processing.crop_image,
    "apply_filter": image_processing.apply_filter,
    "detect_faces": image_processing.detect_faces,
    "extract_text_from_image": image_processing.extract_text_from_image,

    # Media Processing
    "convert_audio": media_processing.convert_audio,
    "trim_audio": media_processing.trim_audio,
    "extract_audio": media_processing.extract_audio_from_video,
    "trim_video": media_processing.trim_video,
    "add_subtitles": media_processing.add_subtitles_to_video,
}

# Advanced Tool Classes (require initialization)
TOOL_CLASSES = {
    "EmailClient": email_calendar.EmailClient,
    "IMAPClient": email_calendar.IMAPClient,
    "GoogleCalendarClient": email_calendar.GoogleCalendarClient,
    "MeetingScheduler": email_calendar.MeetingScheduler,
    "SQLiteClient": database_connectors.SQLiteClient,
    "PostgreSQLClient": database_connectors.PostgreSQLClient,
    "MySQLClient": database_connectors.MySQLClient,
    "MongoDBClient": database_connectors.MongoDBClient,
    "RedisClient": database_connectors.RedisClient,
    "Neo4jClient": database_connectors.Neo4jClient,
    "RESTAPIClient": api_ecosystem.RESTAPIClient,
    "OAuth2Client": api_ecosystem.OAuth2Client,
    "WebhookListener": api_ecosystem.WebhookListener,
    "APIKeyManager": api_ecosystem.APIKeyManager,
    "RateLimiter": api_ecosystem.RateLimiter,
}
