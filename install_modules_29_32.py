import os
import sys
import subprocess

def write_clean(filename, content):
    cleaned = content.replace("\u00a0", " ").replace("\u200b", "")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(cleaned)

# ==============================================================================
# MODULES 29 TO 32: CONSUMER, MACT, IPR & LABOUR SUITES
# ==============================================================================
EXPANDED_ENGINES_CODE = '''import os
import sys
import argparse
from datetime import datetime

# --- MODULE 29: CONSUMER PROTECTION SUITE ---
def generate_consumer_complaint(complainant, opposite_party, defect_desc, compensation_claimed):
    os.makedirs("consumer_petitions", exist_ok=True)
    content = f"""# IN THE DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION AT BENGALURU
CONSUMER COMPLAINT NO. _________ OF 2026

**BETWEEN:**
**{complainant}**                                                  ... COMPLAINANT
**AND:**
**{opposite_party}**                                              ... OPPOSITE PARTY

---
## COMPLAINT UNDER SECTION 35 OF THE CONSUMER PROTECTION ACT, 2019
1. **Nature of Deficiency & Defect:** The Complainant purchased goods/services from the Opposite Party, which suffered from severe manufacturing defects / deficiency in service as detailed: `{defect_desc}`.
2. **Jurisdiction & Valuation:** Total claim value including compensation for mental agony and deficiency is INR {compensation_claimed:,.2f}, falling well within pecuniary jurisdiction.
3. **Relief Claimed:** Refund of purchase price, compensation of INR {compensation_claimed:,.2f}, and litigation costs.
"""
    path = f"consumer_petitions/consumer_complaint_{complainant.replace(' ', '_')}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Success] Consumer Complaint saved -> '{path}'")

# --- MODULE 30: MACT COMPENSATION SUITE ---
def generate_mact_petition(claimant, insurer, accident_date, compensation_amount):
    os.makedirs("mact_petitions", exist_ok=True)
    content = f"""# IN THE MOTOR ACCIDENTS CLAIMS TRIBUNAL AT BENGALURU (MACT)
M.V.C. NO. _________ OF 2026

**BETWEEN:**
**{claimant}**                                                    ... CLAIMANT
**AND:**
1. Driver / Owner of Offending Vehicle
2. **{insurer}** (Insurance Company)                            ... RESPONDENTS

---
## PETITION UNDER SECTION 166 OF THE MOTOR VEHICLES ACT, 1988
1. **Date & Details of Accident:** On `{accident_date}`, due to rash and negligent driving by the offending vehicle driver, the Claimant sustained grievous injuries / permanent disablement.
2. **Compensation Claimed:** Total statutory compensation under pecuniary and non-pecuniary heads: **INR {compensation_amount:,.2f}** with 9% interest per annum from the date of petition.
"""
    path = f"mact_petitions/mact_claim_{claimant.replace(' ', '_')}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Success] MACT Petition saved -> '{path}'")

# --- MODULE 31: IPR & TRADEMARK SUITE ---
def generate_ipr_notice(brand_owner, infringer, trademark_name):
    os.makedirs("ipr_notices", exist_ok=True)
    content = f"""# CEASE & DESIST LEGAL NOTICE (TRADEMARKS ACT, 1999)

**FROM:** Counsel for **{brand_owner}** (Registered Proprietor)
**TO:** **{infringer}**

1. **Proprietary Rights:** Our client is the registered owner of the trademark **"{trademark_name}"** under Class ___ of the Trademarks Act, 1999.
2. **Infringement:** It has come to our notice that you are unauthorizedly using a deceptively similar mark in the course of trade, causing consumer confusion and passing off.
3. **Demand:** Cease all usage, surrender infringing stock, and tender unconditional written apology within **48 hours**, failing which civil suit for permanent injunction and damages will be instituted.
"""
    path = f"ipr_notices/ipr_cease_desist_{brand_owner.replace(' ', '_')}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Success] IPR Notice saved -> '{path}'")

# --- MODULE 32: LABOUR & INDUSTRIAL DISPUTES SUITE ---
def generate_labour_claim(workman, employer, termination_date, back_wages):
    os.makedirs("labour_claims", exist_ok=True)
    content = f"""# BEFORE THE LABOUR COURT / INDUSTRIAL TRIBUNAL AT BENGALURU
REFERENCE NO. (ID) _________ OF 2026

**BETWEEN:**
**{workman}**                                                    ... WORKMAN
**AND:**
**{employer}**                                                    ... MANAGEMENT

---
## STATEMENT OF CLAIM UNDER SECTION 10(4A) OF THE INDUSTRIAL DISPUTES ACT, 1947
1. **Illegal Termination:** The Workman was terminated illegally on `{termination_date}` in flagrant violation of Section 25F (Retrenchment Compensation & Notice) of the Industrial Disputes Act, 1947.
2. **Relief Sought:** Reinstatement with continuity of service, full back wages amounting to **INR {back_wages:,.2f}**, and consequential benefits.
"""
    path = f"labour_claims/labour_claim_{workman.replace(' ', '_')}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Success] Labour Claim saved -> '{path}'")

def handle_consumer_cli(args):
    p = argparse.ArgumentParser(prog="sweety legal consumer")
    p.add_argument("--complainant", default="Sri. Kiran Kumar")
    p.add_argument("--party", default="M/s. Apex Electronics Ltd.")
    p.add_argument("--defect", default="Defective engine/electronic appliance failure within warranty period.")
    p.add_argument("--amount", type=float, default=350000.0)
    a = p.parse_args(args)
    generate_consumer_complaint(a.complainant, a.party, a.defect, a.amount)

def handle_mact_cli(args):
    p = argparse.ArgumentParser(prog="sweety legal mact")
    p.add_argument("--claimant", default="Sri. Ramesh Naik")
    p.add_argument("--insurer", default="ICICI Lombard General Insurance")
    p.add_argument("--date", default="2026-03-15")
    p.add_argument("--amount", type=float, default=1500000.0)
    a = p.parse_args(args)
    generate_mact_petition(a.claimant, a.insurer, a.date, a.amount)

def handle_ipr_cli(args):
    p = argparse.ArgumentParser(prog="sweety legal ipr")
    p.add_argument("--owner", default="M/s. TechVeda Solutions")
    p.add_argument("--infringer", default="M/s. BytePirate Corp")
    p.add_argument("--mark", default="SWEETYAI")
    a = p.parse_args(args)
    generate_ipr_notice(a.owner, a.infringer, a.mark)

def handle_labour_cli(args):
    p = argparse.ArgumentParser(prog="sweety legal labour")
    p.add_argument("--workman", default="Sri. Venkatesh Murthy")
    p.add_argument("--employer", default="M/s. Apex Garments Factory")
    p.add_argument("--term-date", default="2026-02-10")
    p.add_argument("--wages", type=float, default=450000.0)
    a = p.parse_args(args)
    generate_labour_claim(a.workman, a.employer, a.term_date, a.wages)
'''

# ==============================================================================
# UPDATED MASTER ROUTER (32 MODULES)
# ==============================================================================
UNIFIED_SWEETY_32 = '''# --- SWEETYAI HOME-DIRECTORY SANDBOX ENFORCEMENT ---
from sandbox_guard import activate_home_sandbox as _activate_home_sandbox
_activate_home_sandbox()
# ---------------------------------------------------
# SWEETYAI UNIFIED FAST-PATH ROUTER (32 MODULES)

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

    print("=== SWEETYAI ENTERPRISE LEGAL WORKSTATION (32 MODULES COMPLETE) ===")
    print("Usage: python3 sweety.py legal [review | bail | ni138 | stamp-duty | crl-appeal | ibc | arbitration | hc-quash | comm-suit | execution | msme | family-court | consumer | mact | ipr | labour | mobile]")

if __name__ == "__main__":
    main()
'''

write_clean("consumer_motor_labour_engine.py", EXPANDED_ENGINES_CODE)
write_clean("sweety.py", UNIFIED_SWEETY_32)

for fname in ("consumer_motor_labour_engine.py", "sweety.py"):
    with open(fname, "rb") as f:
        compile(f.read(), fname, "exec")
print("[Compile Check] Modules 29-32 and sweety.py compiled successfully!")

print("\n=== [TEST] Running New Modules (Consumer, MACT, IPR, Labour) ===")
subprocess.run(["python3", "sweety.py", "legal", "consumer"], check=True)
subprocess.run(["python3", "sweety.py", "legal", "mact"], check=True)
subprocess.run(["python3", "sweety.py", "legal", "ipr"], check=True)
subprocess.run(["python3", "sweety.py", "legal", "labour"], check=True)
