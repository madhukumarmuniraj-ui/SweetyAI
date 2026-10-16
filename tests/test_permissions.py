import pytest
from app.security.permissions import PermissionManager, PermissionStatus, PermissionLevel

def test_safe_tools():
    pm = PermissionManager()
    for tool in ["calculator", "list_files", "read_file", "get_current_time", "read_clipboard_text", "get_system_info"]:
        decision = pm.check(tool)
        assert decision.status == PermissionStatus.ALLOWED
        assert decision.level == PermissionLevel.SAFE

def test_approval_tools():
    pm = PermissionManager()
    for tool in ["write_file", "delete_memory", "write_clipboard_text", "open_application", "generate_legal_document"]:
        decision = pm.check(tool)
        assert decision.status == PermissionStatus.ASK
        assert decision.level == PermissionLevel.APPROVAL

def test_dangerous_tools():
    pm = PermissionManager()
    for tool in ["delete_file", "run_command", "format_drive"]:
        decision = pm.check(tool)
        assert decision.status == PermissionStatus.ASK
        assert decision.level == PermissionLevel.DANGEROUS

def test_unclassified_tools():
    pm = PermissionManager()
    decision = pm.check("unknown_arbitrary_tool_xyz")
    assert decision.status == PermissionStatus.DENIED
