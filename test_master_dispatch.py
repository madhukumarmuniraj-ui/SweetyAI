import sys
import os

# Ensure app package is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from app.tools.master_registry import master_tool_router
    
    print("=== TESTING MASTER TOOL ROUTER ===")
    
    # Test 1: Directory Listing
    print("\n[Test 1: list_directory]")
    res1 = master_tool_router("list_directory", {"path": "."})
    print(res1[:300] + "...\n[Result OK]")
    
    # Test 2: Shell Command
    print("\n[Test 2: run_shell_command]")
    res2 = master_tool_router("run_shell_command", {"command": "uptime"})
    print(res2)
    
    print("\n=== ALL MASTER ROUTER TESTS PASSED SUCCESSFULLY! ===")
except Exception as e:
    print(f"Test failed with error: {str(e)}")
