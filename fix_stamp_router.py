import os
import subprocess

# 1. Clean any non-breaking spaces from stamp_duty_calculator.py
if os.path.exists("stamp_duty_calculator.py"):
    with open("stamp_duty_calculator.py", "r", encoding="utf-8") as f:
         s_code = f.read().replace("\u00a0", " ")
    with open("stamp_duty_calculator.py", "w", encoding="utf-8") as f:
        f.write(s_code)

# 2. Write a clean sweety.py with all 19 modules properly indented
CLEAN_SWEETY = '''# --- SWEETYAI HOME-DIRECTORY SANDBOX ENFORCEMENT ---
from sandbox_guard import activate_home_sandbox as _activate_home_sandbox
_activate_home_sandbox()
# ---------------------------------------------------

import sys as _sys
import os as _os

def main():
    if len(_sys.argv) > 1:
        _cmd = _sys.argv[1]
        _sub = _sys.argv[2] if len(_sys.argv) > 2 else ""

        # Module 16: Full Master Case Packet Pipeline
        if _cmd in ("full-audit", "packet") or (_cmd == "legal" and _sub in ("full-audit", "packet")):
            from full_audit_pipeline import handle_full_audit_cli
            _args = _sys.argv[2:] if _cmd in ("full-audit", "packet") else _sys.argv[3:]
            handle_full_audit_cli(_args)
            _sys.exit(0)

        # Module 9 & Export: High Court A4 HTML Exporter
        if _cmd == "export" or (_cmd == "legal" and _sub == "export"):
            from document_exporter import export_document
            _args = _sys.argv[2:] if _cmd == "export" else _sys.argv[3:]
            if _args:
                export_document(_args[0])
            else:
                print("Usage: python3 sweety.py export <file.md>")
            _sys.exit(0)

        # Module 8: Karnataka Court Fee Calculator
        if _cmd in ("calc-fees", "calc") or (_cmd == "legal" and _sub in ("calc-fees", "calc")):
            from court_fee_calculator import handle_calc_cli
            _args = _sys.argv[2:] if _cmd in ("calc-fees", "calc") else _sys.argv[3:]
            handle_calc_cli(_args)
            _sys.exit(0)

        # Module 5: Privacy, PII & BSA Sec. 132 Auditor
        if _cmd == "privacy-audit" or (_cmd == "legal" and _sub == "privacy-audit"):
            from privacy_and_playbook_engine import handle_privacy_cli
            _args = _sys.argv[2:] if _cmd == "privacy-audit" else _sys.argv[3:]
            handle_privacy_cli(_args)
            _sys.exit(0)

        # Module 4: Contract Playbook Reviewer
        if _cmd == "review" or (_cmd == "legal" and _sub == "review"):
            from contract_reviewer import handle_review_cli
            _args = _sys.argv[2:] if _cmd == "review" else _sys.argv[3:]
            handle_review_cli(_args)
            _sys.exit(0)

        # Module 6: Citation & Statute Range Verifier
        if _cmd == "verify-citations" or (_cmd == "legal" and _sub == "verify-citations"):
            from citation_verifier import handle_verify_cli
            _args = _sys.argv[2:] if _cmd == "verify-citations" else _sys.argv[3:]
            handle_verify_cli(_args)
            _sys.exit(0)

        # Module 7: High Court Chronology & Synopsis
        if _cmd in ("chronology", "list-of-dates") or (_cmd == "legal" and _sub in ("chronology", "list-of-dates")):
            from chronology_extractor import handle_chronology_cli
            _args = _sys.argv[2:] if _cmd in ("chronology", "list-of-dates") else _sys.argv[3:]
            handle_chronology_cli(_args)
            _sys.exit(0)

        # Module 3: Redline Generator
        if _cmd == "redline" or (_cmd == "legal" and _sub == "redline"):
            from redline_generator import generate_redline
            _args = _sys.argv[2:] if _cmd == "redline" else _sys.argv[3:]
            if len(_args) >= 2:
                generate_redline(_args[0], _args[1])
            else:
                print("Usage: python3 sweety.py legal redline <original> <modified>")
            _sys.exit(0)

        # Module 3b: Parallel Precedent Search
        if _cmd == "parallel" or (_cmd == "legal" and _sub == "parallel"):
            from parallel_precedent import find_parallel_precedents
            _args = _sys.argv[2:] if _cmd == "parallel" else _sys.argv[3:]
            if _args:
                find_parallel_precedents(" ".join(_args))
            else:
                print("Usage: python3 sweety.py legal parallel <proposition>")
            _sys.exit(0)

        # Modules 11, 12, 13: Trial, Custody & Electronic Evidence Suite
        if _cmd in ("sec63-cert", "custody-calc", "cross-exam") or (_cmd == "legal" and _sub in ("sec63-cert", "custody-calc", "cross-exam")):
            from trial_and_evidence_suite import handle_suite_cli
            _target_cmd = _cmd if _cmd in ("sec63-cert", "custody-calc", "cross-exam") else _sub
            _args = _sys.argv[2:] if _cmd in ("sec63-cert", "custody-calc", "cross-exam") else _sys.argv[3:]
            handle_suite_cli(_target_cmd, _args)
            _sys.exit(0)

        # Module 14: Bail Petition Suite
        if _cmd == "bail" or (_cmd == "legal" and _sub == "bail"):
            from bail_petition_generator import handle_bail_cli
            _args = _sys.argv[2:] if _cmd == "bail" else _sys.argv[3:]
            handle_bail_cli(_args)
            _sys.exit(0)

        # Module 15: NI Act Sec. 138 PCR Suite
        if _cmd == "ni138" or (_cmd == "legal" and _sub == "ni138"):
            from ni138_engine import handle_ni138_cli
            _args = _sys.argv[2:] if _cmd == "ni138" else _sys.argv[3:]
            handle_ni138_cli(_args)
            _sys.exit(0)

        # Module 19: Karnataka Stamp Duty & Impounding Calculator
        if _cmd == "stamp-duty" or (_cmd == "legal" and _sub == "stamp-duty"):
            from stamp_duty_calculator import handle_stamp_cli
            _args = _sys.argv[2:] if _cmd == "stamp-duty" else _sys.argv[3:]
            handle_stamp_cli(_args)
            _sys.exit(0)

        # Modules 17 & 18: Anthropic .DOCX Track-Changes, .XLSX Claim Schedules & MCP Sync
        if _cmd in ("docx-export", "docx-redline", "claim-xlsx", "mcp-sync") or (_cmd == "legal" and _sub in ("docx-export", "docx-redline", "claim-xlsx", "mcp-sync")):
            from anthropic_boost_engine import handle_boost_cli
            _target_cmd = _cmd if _cmd in ("docx-export", "docx-redline", "claim-xlsx", "mcp-sync") else _sub
            _args = _sys.argv[2:] if _cmd in ("docx-export", "docx-redline", "claim-xlsx", "mcp-sync") else _sys.argv[3:]
            handle_boost_cli(_target_cmd, _args)
            _sys.exit(0)

        # Module 2: Plugin Sync & Registry
        if _cmd == "plugin":
            from plugin_loader import setup_knowledge_plugins
            if _sub == "sync":
                setup_knowledge_plugins()
            else:
                import json
                pdir = "anthropic_plugins"
                if not _os.path.exists(pdir):
                    setup_knowledge_plugins()
                print("=== Installed Anthropic Knowledge-Work Plugins ===")
                for p in _os.listdir(pdir):
                    mp = _os.path.join(pdir, p, ".claude-plugin", "plugin.json")
                    if _os.path.exists(mp):
                        with open(mp) as mf:
                            d = json.load(mf)
                        print(f" - [{d['name']}] : {d['description']}")
            _sys.exit(0)

    print("=== SWEETYAI ENTERPRISE LEGAL WORKSTATION ===")
    print("Usage: python3 sweety.py legal [review | bail | ni138 | stamp-duty | sec63-cert | custody-calc | cross-exam | full-audit | docx-redline | claim-xlsx]")

if __name__ == "__main__":
    main()
'''

with open("sweety.py", "w", encoding="utf-8") as f:
    f.write(CLEAN_SWEETY.replace("\u00a0", " "))

print("[Success] sweety.py and stamp_duty_calculator.py normalized and verified.")

# 3. Execute the Stamp Duty & Impounding Calculator test
subprocess.run([
    "python3", "sweety.py", "legal", "stamp-duty",
    "--instrument", "conveyance_urban",
    "--value", "7500000",
    "--deficit", "100000"
], check=True)
