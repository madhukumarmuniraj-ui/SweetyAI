import os
import glob
import subprocess
import json
import urllib.request
import urllib.parse
from html.parser import HTMLParser

# Import existing modules safely if present
try:
    from app.tools.statute_mapper import map_statute
except ImportError:
    def map_statute(query: str) -> str:
        return f"Statute mapper fallback for: {query}"

class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
    def handle_data(self, data):
        t = data.strip()
        if t:
            self.text.append(t)

def master_tool_router(tool_name: str, arguments: dict) -> str:
    """Universal router that executes the requested tool locally with error boundaries."""
    try:
        if tool_name == "map_statute":
            return map_statute(arguments.get("query", ""))
            
        elif tool_name == "read_file":
            path = arguments.get("path", "")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()[:5000]
            return f"File does not exist: {path}"
            
        elif tool_name == "list_directory":
            dir_path = arguments.get("path", ".")
            items = os.listdir(dir_path)
            return f"Directory listing of {dir_path}:\n" + "\n".join([f" - {i}" for i in sorted(items)])
            
        elif tool_name == "run_shell_command":
            cmd = arguments.get("command", "")
            dangerous = ["rm -rf /", "mkfs", ":(){ :|:& };:"]
            if any(d in cmd for d in dangerous):
                return "Blocked by security policy."
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            return res.stdout if res.returncode == 0 else res.stderr
            
        elif tool_name == "read_webpage":
            url = arguments.get("url", "")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
            parser = HTMLTextExtractor()
            parser.feed(html)
            return " ".join(parser.text)[:3000]
            
        else:
            return f"Unknown tool requested: {tool_name}"
            
    except Exception as e:
        return f"Tool execution error in {tool_name}: {str(e)}"
