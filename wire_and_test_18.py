import os
import sys
import time
import subprocess

START_TAG = "# --- SWEETYAI UNIFIED FAST-PATH ROUTER (START) ---"
END_TAG = "# --- SWEETYAI UNIFIED FAST-PATH ROUTER (END) ---"

BOOST_HOOK = """    if _cmd in ("docx-export", "docx-redline", "claim-xlsx", "mcp-sync") or (_cmd == "legal" and _sub in ("docx-export", "docx-redline", "claim-xlsx", "mcp-sync")):
        from anthropic_boost_engine import handle_boost_cli
        _target_cmd = _cmd if _cmd in ("docx-export", "docx-redline", "claim-xlsx", "mcp-sync") else _sub
        _args = _sys.argv[2:] if _cmd in ("docx-export", "docx-redline", "claim-xlsx", "mcp-sync") else _sys.argv[3:]
        handle_boost_cli(_target_cmd, _args)
        _sys.exit(0)
"""

with open("sweety.py", "r", encoding="utf-8") as f:
    code = f.read().replace("\u00a0", " ")

if "from anthropic_boost_engine import handle_boost_cli" not in code:
    code = code.replace(END_TAG, BOOST_HOOK + END_TAG)
    with open("sweety.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("[Success] Anthropic .DOCX Track-Changes, .XLSX Claim Engine & MCP Registry wired into sweety.py!")

# Run live verification of the new Anthropic Boost engines
subprocess.run(["python3", "sweety.py", "legal", "docx-redline", "sample_contract.txt", "modified_contract.txt"], check=True)
subprocess.run(["python3", "sweety.py", "legal", "docx-export", "valuation_slips/valuation_slip_commercial_2500000.md"], check=True)
subprocess.run(["python3", "sweety.py", "legal", "claim-xlsx", "--principal", "2500000", "--rate", "18", "--start-date", "2025-01-15", "--regime", "sec34_cpc"], check=True)
subprocess.run(["python3", "sweety.py", "legal", "mcp-sync"], check=True)
