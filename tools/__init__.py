import datetime
import os
import glob

# Import SweetyAI's core modular tools
from .calculator import calculator
from .filesystem import list_files, read_file
from .search_project import search_project
from .webpage import web_search
from .write_file import write_file

def get_current_time():
    """Returns the current date and time on the local machine."""
    now = datetime.datetime.now()
    return now.strftime("%A, %B %d, %Y, %I:%M %p")

def open_workspace_folder():
    """Opens the local knowledge base documents folder in Windows Explorer."""
    folder_path = os.path.abspath("./knowledge_base_docs")
    os.makedirs(folder_path, exist_ok=True)
    try:
        os.startfile(folder_path)
        return "Opened the local workspace folder successfully."
    except Exception as e:
        return f"Could not open folder: {str(e)}"

def list_knowledge_documents():
    """Lists all files currently indexed in the local RAG knowledge base."""
    folder_path = "./knowledge_base_docs"
    if not os.path.exists(folder_path):
        return "No knowledge base directory found."
    files = os.listdir(folder_path)
    if not files:
        return "The knowledge base is currently empty."
    return "Indexed documents: " + ", ".join(files)

def search_local_files(query):
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

# Central Registry mapping all core and utility tools for SweetyAI
AVAILABLE_TOOLS = {
    "calculator": calculator,
    "list_files": list_files,
    "read_file": read_file,
    "search_project": search_project,
    "web_search": web_search,
    "write_file": write_file,
    "get_current_time": get_current_time,
    "open_workspace_folder": open_workspace_folder,
    "list_knowledge_documents": list_knowledge_documents,
    "search_local_files": search_local_files
}