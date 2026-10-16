import pyperclip

def read_clipboard_text() -> str:
    """Reads the current text from the system clipboard."""
    try:
        text = pyperclip.paste()
        if not text or not text.strip():
            return "The clipboard is currently empty."
        return text
    except Exception as e:
        return f"Failed to read clipboard: {str(e)}"

def write_clipboard_text(content: str) -> str:
    """Writes the given text to the system clipboard."""
    try:
        pyperclip.copy(content)
        return "Text copied to clipboard successfully."
    except Exception as e:
        return f"Failed to write to clipboard: {str(e)}"
