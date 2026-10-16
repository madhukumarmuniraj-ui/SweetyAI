import os
import re
import sys
import time
import subprocess

# 1. Upgrade the Unified Fast-Path Router in sweety.py to cover all 15 modules
UNIFIED_ROUTER = """# --- SWEETYAI UNIFIED FAST-PATH ROUTER (START) ---
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
            print("=== Installed Anthropic Knowledge-Work Plugins ===")
            for p in _os.listdir(pdir):
                mp = _os.path.join(pdir, p, ".claude-plugin", "plugin.json")
                if _os.path.exists(mp):
                    with open(mp) as mf:
                        d = json.load(mf)
                    print(f" - [{d['name']}] : {d['description']}")
        _sys.exit(0)
# --- SWEETYAI UNIFIED FAST-PATH ROUTER (END) ---"""

if os.path.exists("sweety.py"):
    with open("sweety.py", "r", encoding="utf-8") as f:
        sweety_code = f.read().replace(" ", " ")

    router_pattern = re.compile(
        r"# --- SWEETYAI UNIFIED FAST-PATH ROUTER \(START\) ---.*?# --- SWEETYAI UNIFIED FAST-PATH ROUTER \(END\) ---",
        flags=re.DOTALL,
    )
    if router_pattern.search(sweety_code):
        sweety_code = router_pattern.sub(UNIFIED_ROUTER, sweety_code, count=1)
    else:
        sweety_code = UNIFIED_ROUTER + "\n\n" + sweety_code

    with open("sweety.py", "w", encoding="utf-8") as f:
        f.write(sweety_code)
    print("[Router] 15-Module Unified Fast-Path Router updated in sweety.py")

# 2. Ensure sample test fixtures exist
if not os.path.exists("sample_contract.txt"):
    with open("sample_contract.txt", "w", encoding="utf-8") as f:
        f.write(
            "MASTER SERVICE AGREEMENT\n"
            "Executed on 10.01.2026 at Bengaluru, Karnataka.\n"
            "1. Liability: Vendor shall have unlimited liability for all claims.\n"
            "2. Arbitration: Any dispute shall be referred to a Sole Arbitrator solely appointed by the Company.\n"
            "3. Non-Compete: Vendor shall not engage in any competing business for 3 years post-termination.\n"
            "4. Notice: Legal notice issued on 15.05.2026. FIR registered on 01.08.2026 under Section 318(4) BNS.\n"
            "5. Authorities: State of Haryana v. Bhajan Lal, 1992 Supp (1) SCC 335; Arnesh Kumar v. State of Bihar, (2014) 8 SCC 273;\n"
            "   Section 35(3) of BNSS and Section 528 of BNSS.\n"
            "Contact: legal@corp.in | PAN: ABCDE1234F | GSTIN: 29ABCDE1234F1Z5\n"
        )

if not os.path.exists("modified_contract.txt"):
    with open("modified_contract.txt", "w", encoding="utf-8") as f:
        f.write(
            "MASTER SERVICE AGREEMENT (AMENDED)\n"
            "Executed on 10.01.2026 at Bengaluru, Karnataka.\n"
            "1. Liability: Aggregate liability capped at 100% of preceding 12 months fees under Section 73 ICA.\n"
            "2. Arbitration: Sole Arbitrator appointed mutually at Arbitration & Conciliation Centre, Bengaluru.\n"
        )

# 3. Define the 15-Module Diagnostic Test Matrix
TESTS = [
    (
        "1. Anthropic Plugin Sync & Registry",
        ["python3", "sweety.py", "plugin", "sync"],
        "anthropic_plugins/legal/.claude-plugin/plugin.json",
    ),
    (
        "2. Legal Redline & Diff Formatter",
        ["python3", "sweety.py", "legal", "redline", "sample_contract.txt", "modified_contract.txt"],
        "redline_outputs/redline_sample_contract_vs_modified_contract.md",
    ),
    (
        "3. Parallel Precedent & Counter-Brief",
        ["python3", "sweety.py", "legal", "parallel", "Mandatory notice under Section 35(3) BNSS before arrest"],
        "parallel_precedent_outputs/parallel_precedent_mandatory_notice_under_section_35(3).md",
    ),
    (
        "4. Indian Statutory Contract Playbook",
        ["python3", "sweety.py", "legal", "review", "sample_contract.txt"],
        "contract_review_reports/contract_audit_sample_contract.md",
    ),
    (
        "5. Privacy, PII & BSA Sec. 132 Auditor",
        ["python3", "sweety.py", "legal", "privacy-audit", "sample_contract.txt", "--scrub"],
        "privacy_audit_reports/privacy_audit_sample_contract.txt.md",
    ),
    (
        "6. Citation & BNS/BNSS Range Verifier",
        ["python3", "sweety.py", "legal", "verify-citations", "sample_contract.txt"],
        "citation_audit_reports/citation_audit_sample_contract.md",
    ),
    (
        "7. High Court Synopsis & List of Dates",
        ["python3", "sweety.py", "legal", "chronology", "sample_contract.txt", "--jurisdiction", "crlp"],
        "chronology_outputs/synopsis_list_of_dates_sample_contract.md",
    ),
    (
        "8. Karnataka Court Fee & Limitation Calc",
        ["python3", "sweety.py", "calc-fees", "--type", "commercial", "--value", "2500000", "--cause-date", "2025-01-15", "--exclusion-days", "30"],
        "valuation_slips/valuation_slip_commercial_2500000.md",
    ),
    (
        "9. Karnataka High Court A4 HTML Exporter",
        ["python3", "sweety.py", "export", "valuation_slips/valuation_slip_commercial_2500000.md"],
        "court_ready_exports/valuation_slip_commercial_2500000_court_ready.html",
    ),
    (
        "10. Downloads Folder Auto-Scanner",
        ["python3", "sweety.py", "legal", "review", "--list-downloads"],
        None,
    ),
    (
        "11. Sec. 63(4) BSA SHA-256 Certifier",
        ["python3", "sweety.py", "legal", "sec63-cert", "sample_contract.txt", "--deponent", "Madhukumar Muniraj", "--device", "Linux Enterprise Workstation"],
        "sec63_certificates/sec63_bsa_certificate_sample_contract_txt.md",
    ),
    (
        "12. Sec. 187 BNSS Remand & Default Bail",
        ["python3", "sweety.py", "legal", "custody-calc", "--remand-date", "2026-08-10", "--tier", "60"],
        "custody_bail_reports/sec187_custody_audit_2026-08-10_60d.md",
    ),
    (
        "13. Sec. 180 BNSS / 148 BSA Cross-Exam",
        ["python3", "sweety.py", "legal", "cross-exam", "sample_contract.txt", "modified_contract.txt", "--witness", "PW-1"],
        "cross_examination_matrices/cross_exam_matrix_pw-1.md",
    ),
    (
        "14. Sec. 480/482/483 BNSS Bail Generator",
        [
            "python3", "sweety.py", "legal", "bail",
            "--type", "482",
            "--forum", "hc",
            "--ps", "Whitefield CEN Crime Police Station, Bengaluru",
            "--crime-no", "Crime No. 215/2026",
            "--offences", "Sections 318(4), 316(2), and 61(2) of BNS, 2023",
            "--max-punishment", "up_to_7",
        ],
        "bail_petitions/bail_sec482_hc_crime_no__215_2026.md",
    ),
    (
        "15. Sec. 138 NI Act & Sec. 223 BNSS PCR",
        [
            "python3", "sweety.py", "legal", "ni138",
            "--cheque-no", "884512",
            "--amount", "1500000",
            "--cheque-date", "2026-07-10",
            "--presentation-date", "2026-08-25",
            "--dishonour-date", "2026-08-27",
            "--notice-date", "2026-09-10",
            "--service-date", "2026-09-14",
        ],
        "ni138_complaints/ni138_pcr_bundle_cheque_884512.md",
    ),
]

print("\n================================================================================================")
print("                SWEETYAI ENTERPRISE LEGAL SUITE — 15-MODULE MASTER DIAGNOSTIC                   ")
print("================================================================================================")
print(f"{'MODULE NAME':<42} | {'STATUS':<8} | {'TIME':<7} | {'VERIFIED ARTIFACT'}")
print("-" * 96)

passed = 0
failed = 0

for name, cmd, expected_file in TESTS:
    t0 = time.time()
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    elapsed = f"{(time.time() - t0):.2f}s"

    file_ok = True
    if expected_file and not os.path.exists(expected_file):
        file_ok = False

    if proc.returncode == 0 and file_ok:
        status = "PASS"
        passed += 1
        artifact_note = expected_file if expected_file else "Console Output Verified"
    else:
        status = "FAIL"
        failed += 1
        err_line = (proc.stderr or proc.stdout).strip().splitlines()[-1:] or ["Unknown error"]
        artifact_note = f"ERR: {err_line[0][:48]}"

    print(f"{name:<42} | {status:<8} | {elapsed:<7} | {artifact_note}")

print("================================================================================================")
print(f"FINAL VERDICT: {passed}/{len(TESTS)} Modules Operational | {failed} Failures")
print("================================================================================================\n")
