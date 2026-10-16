# tests/test_main.py
from pathlib import Path
from hermes_tools import read_file, write_file, terminal, patch

def test_read_file(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text("Hello World")
    result = read_file(path=path)
    assert result["content"] == "Hello World\\n"
