import os

def write_file(filename: str, content: str):
    """Overwrites a file with new content. Creates it if it doesn't exist."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote/overwrote {filename}"
    except Exception as e:
        return f"Write error: {e}"

def read_file(filename: str):
    """Reads the content of a file."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Read error: {e}"

def append_file(filename: str, content: str):
    """Adds content to the END of an existing file (Modify/Edit)."""
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write("\n" + content)
        return f"Successfully appended to {filename}"
    except Exception as e:
        return f"Append error: {e}"

def delete_file(filename: str):
    """Deletes a file from the system."""
    try:
        if os.path.exists(filename):
            os.remove(filename)
            return f"Successfully deleted {filename}"
        else:
            return f"Error: File {filename} does not exist."
    except Exception as e:
        return f"Delete error: {e}"

def list_files(path="."):
    """Lists all files in a directory."""
    try:
        return str(os.listdir(path))
    except Exception as e:
        return f"List error: {e}"
