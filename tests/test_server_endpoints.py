import pytest
from app.tools import AVAILABLE_TOOLS, get_system_info, list_knowledge_documents, calculator

def test_available_tools_has_all_features():
    expected_tools = [
        "calculator",
        "list_files",
        "read_file",
        "write_file",
        "search_project",
        "web_search",
        "search_searxng",
        "read_webpage",
        "get_current_time",
        "open_workspace_folder",
        "list_knowledge_documents",
        "search_local_files",
        "read_clipboard_text",
        "write_clipboard_text",
        "generate_legal_document",
        "open_application",
        "get_system_info"
    ]
    for tool_name in expected_tools:
        assert tool_name in AVAILABLE_TOOLS, f"Missing tool: {tool_name}"

def test_direct_tool_invocations():
    # Calculator
    calc_res = AVAILABLE_TOOLS["calculator"](expression="10 + 25 * 2")
    assert "60" in calc_res

    # System Info
    info = AVAILABLE_TOOLS["get_system_info"]()
    assert "System Information" in info or "CPU" in info

    # Current Time
    time_str = AVAILABLE_TOOLS["get_current_time"]()
    assert len(time_str) > 5

    # Knowledge documents listing
    docs = AVAILABLE_TOOLS["list_knowledge_documents"]()
    assert isinstance(docs, str)
