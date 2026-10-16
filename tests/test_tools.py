import pytest
import os
from app.tools.calculator import calculator
from app.tools.filesystem import list_files, read_file, safe_path
from app.tools.desktop_automation import get_system_info, open_application
from app.tools.clipboard import read_clipboard_text, write_clipboard_text
from app.tools import get_current_time, AVAILABLE_TOOLS

def test_calculator():
    assert calculator("2 + 2") == "4"
    assert calculator("10 * 5 - 4") == "46"
    assert "Error" in calculator("import os")

def test_get_current_time():
    time_str = get_current_time()
    assert isinstance(time_str, str)
    assert len(time_str) > 5

def test_safe_path_sandboxing():
    # Inside working dir should succeed
    p = safe_path("package.json")
    assert os.path.exists(p)

    # Outside working dir should raise PermissionError
    with pytest.raises(PermissionError):
        safe_path("../../../Windows/System32/calc.exe")

def test_system_info():
    info = get_system_info()
    assert "System Information" in info
    assert "OS:" in info

def test_available_tools_registry():
    assert "calculator" in AVAILABLE_TOOLS
    assert "list_files" in AVAILABLE_TOOLS
    assert "read_file" in AVAILABLE_TOOLS
    assert "web_search" in AVAILABLE_TOOLS
    assert "search_searxng" in AVAILABLE_TOOLS
    assert "get_system_info" in AVAILABLE_TOOLS
    assert "read_clipboard_text" in AVAILABLE_TOOLS
