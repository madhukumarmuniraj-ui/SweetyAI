# --- SWEETYAI UNIFIED FAST-PATH ROUTER (START) ---
import sys as _sys
if len(_sys.argv) > 1:
    _cmd = _sys.argv[1]
    _sub = _sys.argv[2] if len(_sys.argv) > 2 else ""

    if _cmd == "export" or (_cmd == "legal" and _sub == "export"):
        from document_exporter import export_document
        _args = _sys.argv[2:] if _cmd == "export" else _sys.argv[3:]
        if _args:
            export_document(_args[0])
        else:
            print("Usage: python3 sweety.py export <file.md>")
        _sys.exit(0)

    if _cmd in ("calc-fees", "calc") or (_cmd == "legal" and _sub in ("calc-fees", "calc")):
        from court_fee_calculator import handle_calc_cli
        _args = _sys.argv[2:] if _cmd in ("calc-fees", "calc") else _sys.argv[3:]
        handle_calc_cli(_args)
        _sys.exit(0)

    if _cmd == "privacy-audit" or (_cmd == "legal" and _sub == "privacy-audit"):
        from privacy_and_playbook_engine import handle_privacy_cli
        _args = _sys.argv[2:] if _cmd == "privacy-audit" else _sys.argv[3:]
        handle_privacy_cli(_args)
        _sys.exit(0)

    if _cmd == "review" or (_cmd == "legal" and _sub == "review"):
        from contract_reviewer import handle_review_cli
        _args = _sys.argv[2:] if _cmd == "review" else _sys.argv[3:]
        handle_review_cli(_args)
        _sys.exit(0)

    if _cmd == "verify-citations" or (_cmd == "legal" and _sub == "verify-citations"):
        from citation_verifier import handle_verify_cli
        _args = _sys.argv[2:] if _cmd == "verify-citations" else _sys.argv[3:]
        handle_verify_cli(_args)
        _sys.exit(0)

    if _cmd in ("chronology", "list-of-dates") or (_cmd == "legal" and _sub in ("chronology", "list-of-dates")):
        from chronology_extractor import handle_chronology_cli
        _args = _sys.argv[2:] if _cmd in ("chronology", "list-of-dates") else _sys.argv[3:]
        handle_chronology_cli(_args)
        _sys.exit(0)

    if _cmd == "redline" or (_cmd == "legal" and _sub == "redline"):
        from redline_generator import generate_redline
        _args = _sys.argv[2:] if _cmd == "redline" else _sys.argv[3:]
        if len(_args) >= 2:
            generate_redline(_args[0], _args[1])
        else:
            print("Usage: python3 sweety.py legal redline <original> <modified>")
        _sys.exit(0)

    if _cmd == "parallel" or (_cmd == "legal" and _sub == "parallel"):
        from parallel_precedent import find_parallel_precedents
        _args = _sys.argv[2:] if _cmd == "parallel" else _sys.argv[3:]
        if _args:
            find_parallel_precedents(" ".join(_args))
        else:
            print("Usage: python3 sweety.py legal parallel <proposition>")
        _sys.exit(0)

    if _cmd in ("sec63-cert", "custody-calc", "cross-exam") or (_cmd == "legal" and _sub in ("sec63-cert", "custody-calc", "cross-exam")):
        from trial_and_evidence_suite import handle_suite_cli
        _target_cmd = _cmd if _cmd in ("sec63-cert", "custody-calc", "cross-exam") else _sub
        _args = _sys.argv[2:] if _cmd in ("sec63-cert", "custody-calc", "cross-exam") else _sys.argv[3:]
        handle_suite_cli(_target_cmd, _args)
        _sys.exit(0)

    if _cmd == "bail" or (_cmd == "legal" and _sub == "bail"):
        from bail_petition_generator import handle_bail_cli
        _args = _sys.argv[2:] if _cmd == "bail" else _sys.argv[3:]
        handle_bail_cli(_args)
        _sys.exit(0)

    if _cmd == "ni138" or (_cmd == "legal" and _sub == "ni138"):
        from ni138_engine import handle_ni138_cli
        _args = _sys.argv[2:] if _cmd == "ni138" else _sys.argv[3:]
        handle_ni138_cli(_args)
        _sys.exit(0)

    if _cmd == "plugin":
        from plugin_loader import setup_knowledge_plugins
        if _sub == "sync":
            setup_knowledge_plugins()
        else:
            import json, os as _os
            pdir = "anthropic_plugins"
            if not _os.path.exists(pdir):
                setup_knowledge_plugins()
            print("\n=== Installed Anthropic Knowledge-Work Plugins ===")
            for p in _os.listdir(pdir):
                mp = _os.path.join(pdir, p, ".claude-plugin", "plugin.json")
                if _os.path.exists(mp):
                    with open(mp) as mf:
                        d = json.load(mf)
                    print(f" - [{d['name']}] : {d['description']}")
        _sys.exit(0)
# --- SWEETYAI UNIFIED FAST-PATH ROUTER (END) ---

# --- SWEETYAI HOME-DIRECTORY SANDBOX ENFORCEMENT ---
from sandbox_guard import activate_home_sandbox as _activate_home_sandbox
_activate_home_sandbox()
# ---------------------------------------------------
# SWEETYAI UNIFIED FAST-PATH ROUTER (36 MODULES)

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

        # Module 20: Criminal Appeal & Sec. 430 BNSS Suspension of Sentence Suite
        if _cmd == "crl-appeal" or (_cmd == "legal" and _sub == "crl-appeal"):
            from crl_appeal_engine import handle_crl_appeal_cli
            _args = _sys.argv[2:] if _cmd == "crl-appeal" else _sys.argv[3:]
            handle_crl_appeal_cli(_args)
            _sys.exit(0)

        # Module 21: NCLT / IBC Section 8 & 9 Operational Creditor Suite
        if _cmd == "ibc" or (_cmd == "legal" and _sub == "ibc"):
            from ibc_engine import handle_ibc_cli
            _args = _sys.argv[2:] if _cmd == "ibc" else _sys.argv[3:]
            handle_ibc_cli(_args)
            _sys.exit(0)

        # Module 22: Arbitration Act Sec. 21, Sec. 9 & Sec. 11(6) C.M.P. Suite
        if _cmd == "arbitration" or (_cmd == "legal" and _sub == "arbitration"):
            from arbitration_engine import handle_arbitration_cli
            _args = _sys.argv[2:] if _cmd == "arbitration" else _sys.argv[3:]
            handle_arbitration_cli(_args)
            _sys.exit(0)

        # Module 23: High Court Sec. 528 BNSS Quashing & Art. 226/227 Writ Suite
        if _cmd == "hc-quash" or (_cmd == "legal" and _sub == "hc-quash"):
            from hc_quashing_writ_engine import handle_hc_quash_cli
            _args = _sys.argv[2:] if _cmd == "hc-quash" else _sys.argv[3:]
            handle_hc_quash_cli(_args)
            _sys.exit(0)

        # Module 24: Commercial Courts Act Sec. 12A PIM, Plaint & Statement of Truth Suite
        if _cmd == "comm-suit" or (_cmd == "legal" and _sub == "comm-suit"):
            from commercial_suit_engine import handle_comm_suit_cli
            _args = _sys.argv[2:] if _cmd == "comm-suit" else _sys.argv[3:]
            handle_comm_suit_cli(_args)
            _sys.exit(0)

        # Module 25: Order XXI Rule 11(2) CPC Execution & Sec. 36 Award Enforcement Suite
        if _cmd == "execution" or (_cmd == "legal" and _sub == "execution"):
            from execution_engine import handle_execution_cli
            _args = _sys.argv[2:] if _cmd == "execution" else _sys.argv[3:]
            handle_execution_cli(_args)
            _sys.exit(0)

        # Module 26: MSMED Act Sec. 18 MSEFC Reference & 3x RBI Compound Interest Suite
        if _cmd == "msme" or (_cmd == "legal" and _sub == "msme"):
            from msme_engine import handle_msme_cli
            _args = _sys.argv[2:] if _cmd == "msme" else _sys.argv[3:]
            handle_msme_cli(_args)
            _sys.exit(0)

        # Module 27: Family Court & Matrimonial Litigation Suite
        if _cmd == "family-court" or (_cmd == "legal" and _sub == "family-court"):
            from family_court_engine import handle_family_cli
            _args = _sys.argv[2:] if _cmd == "family-court" else _sys.argv[3:]
            handle_family_cli(_args)
            _sys.exit(0)

        # Module 29: Consumer Protection Suite
        if _cmd == "consumer" or (_cmd == "legal" and _sub == "consumer"):
            from consumer_motor_labour_engine import handle_consumer_cli
            _args = _sys.argv[2:] if _cmd == "consumer" else _sys.argv[3:]
            handle_consumer_cli(_args)
            _sys.exit(0)

        # Module 30: MACT Compensation Suite
        if _cmd == "mact" or (_cmd == "legal" and _sub == "mact"):
            from consumer_motor_labour_engine import handle_mact_cli
            _args = _sys.argv[2:] if _cmd == "mact" else _sys.argv[3:]
            handle_mact_cli(_args)
            _sys.exit(0)

        # Module 31: IPR & Trademark Suite
        if _cmd == "ipr" or (_cmd == "legal" and _sub == "ipr"):
            from consumer_motor_labour_engine import handle_ipr_cli
            _args = _sys.argv[2:] if _cmd == "ipr" else _sys.argv[3:]
            handle_ipr_cli(_args)
            _sys.exit(0)

        # Module 32: Labour & Industrial Disputes Suite
        if _cmd == "labour" or (_cmd == "legal" and _sub == "labour"):
            from consumer_motor_labour_engine import handle_labour_cli
            _args = _sys.argv[2:] if _cmd == "labour" else _sys.argv[3:]
            handle_labour_cli(_args)
            _sys.exit(0)

        # Module 33: IBC Section 7 Financial Creditor Suite
        if _cmd == "ibc-sec7" or (_cmd == "legal" and _sub == "ibc-sec7"):
            from advanced_litigation_engines import handle_ibc_sec7_cli
            _args = _sys.argv[2:] if _cmd == "ibc-sec7" else _sys.argv[3:]
            handle_ibc_sec7_cli(_args)
            _sys.exit(0)

        # Module 34: Article 226 Constitutional Writ & PIL Suite
        if _cmd == "writ" or (_cmd == "legal" and _sub == "writ"):
            from advanced_litigation_engines import handle_writ_cli
            _args = _sys.argv[2:] if _cmd == "writ" else _sys.argv[3:]
            handle_writ_cli(_args)
            _sys.exit(0)

        # Module 35: Cyber Law & IT Act Suite
        if _cmd == "cyber" or (_cmd == "legal" and _sub == "cyber"):
            from advanced_litigation_engines import handle_cyber_cli
            _args = _sys.argv[2:] if _cmd == "cyber" else _sys.argv[3:]
            handle_cyber_cli(_args)
            _sys.exit(0)

        # Module 36: RERA Act, 2016 Complaint Suite
        if _cmd == "rera" or (_cmd == "legal" and _sub == "rera"):
            from advanced_litigation_engines import handle_rera_cli
            _args = _sys.argv[2:] if _cmd == "rera" else _sys.argv[3:]
            handle_rera_cli(_args)
            _sys.exit(0)

        # Module 37 Pro: Advocate Case Diary, Statutory Deadlines & Daily Briefing
        if _cmd in ("diary", "calendar", "todo") or (_cmd == "legal" and _sub in ("diary", "calendar", "todo")):
            from advocate_diary import handle_diary_cli
            _args = _sys.argv[2:] if _cmd in ("diary", "calendar", "todo") else _sys.argv[3:]
            handle_diary_cli(_args)
            _sys.exit(0)

        # Module 38: Autonomous Multi-Bot Orchestrator, Routine Memory & Payment Gate
        if _cmd in ("agents", "bots", "team") or (_cmd == "legal" and _sub in ("agents", "bots", "team")):
            from sweety_agents import handle_agents_cli
            _args = _sys.argv[2:] if _cmd in ("agents", "bots", "team") else _sys.argv[3:]
            handle_agents_cli(_args)
            _sys.exit(0)

        # Module 39: Filing Forms Suite (Vakalatnama, Appearance & Process Fee Memo)
        if _cmd in ("forms", "vakalatnama", "pf-memo") or (_cmd == "legal" and _sub in ("forms", "vakalatnama", "pf-memo")):
            from filing_forms import handle_forms_cli
            _args = _sys.argv[2:] if _cmd in ("forms", "vakalatnama", "pf-memo") else _sys.argv[3:]
            handle_forms_cli(_args)
            _sys.exit(0)

        # Module 40: Secure Social Media & Messaging Gateway Suite
        if _cmd in ("social", "gateway") or (_cmd == "legal" and _sub in ("social", "gateway")):
            from social_gateway import handle_social_cli
            _args = _sys.argv[2:] if _cmd in ("social", "gateway") else _sys.argv[3:]
            handle_social_cli(_args)
            _sys.exit(0)

        # Mobile Web Portal
        if _cmd in ("mobile", "web", "server") or (_cmd == "legal" and _sub in ("mobile", "web", "server")):
            from mobile_portal import start_portal
            start_portal(8080)
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

    print("=== SWEETYAI ENTERPRISE LEGAL WORKSTATION (36 MODULES COMPLETE) ===")
    print("Usage: python3 sweety.py legal [review | bail | ni138 | stamp-duty | crl-appeal | ibc | arbitration | hc-quash | comm-suit | execution | msme | family-court | consumer | mact | ipr | labour | ibc-sec7 | writ | cyber | rera | mobile]")

if __name__ == "__main__":
    main()
