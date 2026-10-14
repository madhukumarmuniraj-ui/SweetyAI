import os
import sys
import subprocess

def write_clean(filename, content):
    cleaned = content.replace("\u00a0", " ").replace("\u200b", "")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(cleaned)

# ==============================================================================
# 1. MODULE 22: ARBITRATION SEC. 21, SEC. 9 & SEC. 11(6) C.M.P. ENGINE
# ==============================================================================
ARBITRATION_ENGINE_CODE = '''import os
import sys
import argparse
from datetime import datetime, timedelta

OUTPUT_DIR = "arbitration_petitions"

def generate_arbitration_suite(
    claimant,
    respondent,
    contract_date,
    clause_no,
    claim_amount,
    default_date,
    unilateral_clause=True
):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        def_dt = datetime.strptime(default_date, "%Y-%m-%d")
        lim_expiry = def_dt + timedelta(days=365 * 3)
        sec9_90d_deadline = (datetime.now() + timedelta(days=90)).strftime("%d.%m.%Y")
        sec11_30d_expiry = (datetime.now() + timedelta(days=30)).strftime("%d.%m.%Y")
        lim_status = (
            f"VALID under Art. 137 Limitation Act (*BSNL v. Nortel Networks*, (2021) 5 SCC 738) — 3-Year Expiry: {lim_expiry.strftime('%d.%m.%Y')}"
            if datetime.now() <= lim_expiry
            else "EXCEEDS 3 YEARS — Plead continuing cause of action / Sec. 18 Limitation Act acknowledgment"
        )
    except Exception:
        sec9_90d_deadline = "90 Days from Interim Order"
        sec11_30d_expiry = "30 Days from Receipt of Sec. 21 Notice"
        lim_status = "Verify 3-Year Limitation under Art. 137 Limitation Act, 1963"

    core_clause_text = ""
    if unilateral_clause:
        core_clause_text = """
3. **Invalidity of Unilateral Appointment Mechanism (*CORE v. ECI SPIC SMO MCML (JV)*, 2024 INSC 857):**
   Insofar as Clause `{clause_no}` purports to vest unilateral authority in one party or its officers to appoint a Sole Arbitrator or curate a restricted panel, such mechanism is **void ab initio** as being violative of **Article 14 of the Constitution of India** and **Section 12(5) read with the Seventh Schedule** of the Arbitration and Conciliation Act, 1996. While the unilateral appointment procedure is severable and void, the core agreement to refer disputes to arbitration remains valid and binding.
""".format(clause_no=clause_no)

    bundle = f"""# ARBITRATION & CONCILIATION ACT, 1996 — COMPLETE LITIGATION SUITE
**(SECTION 21 INVOCATION NOTICE | SECTION 9 INTERIM PETITION | SECTION 11(6) HIGH COURT C.M.P.)**

## PART I: STATUTORY & CONSTITUTIONAL BENCH COMPLIANCE MATRIX
| Statutory / Judicial Gate | Controlling Provision / Precedent | Computed Status / Deadline |
| :--- | :--- | :--- |
| **Claimant / Petitioner** | Section 2(1)(h) Party | **{claimant}** |
| **Respondent** | Section 2(1)(h) Party | **{respondent}** |
| **Arbitration Agreement** | Clause `{clause_no}` of Agreement dated `{contract_date}` | Seat & Venue: **Bengaluru, Karnataka** |
| **Specified Value in Dispute** | Section 12 Commercial Courts Act, 2015 | **INR {claim_amount:,.2f}** |
| **Limitation Audit (Sec. 21)** | *BSNL v. Nortel Networks*, (2021) 5 SCC 738 | **{lim_status}** |
| **Sec. 11(5) 30-Day Wait Window** | 30 Days from Sec. 21 Notice Delivery | Expires on **{sec11_30d_expiry}** |
| **Sec. 9(2) 90-Day Mandate** | Mandatory Commencement from Interim Order | By **{sec9_90d_deadline}** |
| **Unilateral Clause Audit** | *CORE v. ECI SPIC*, 2024 INSC 857 (5-Judge SC) | **{'Unilateral Mechanism Severed; Neutral ACCB Panel Invoked' if unilateral_clause else 'Mutual Appointment Clause Verified'}** |
| **Stamp Duty Objection Shield** | *In Re: Interplay (7-Judge SC)*, 2023 INSC 1066 | Curable defect; does not bar Sec. 11(6) referral |

---

## PART II: STATUTORY NOTICE INVOKING ARBITRATION UNDER SECTION 21
**BY REGISTERED POST AD / SPEED POST / EMAIL**

**To:**
**{respondent}**
Bengaluru, Karnataka.

**Subject:** **STATUTORY NOTICE INVOKING ARBITRATION UNDER SECTION 21 READ WITH SECTION 11(5) OF THE ARBITRATION AND CONCILIATION ACT, 1996** — Dispute arising under Agreement dated **{contract_date}** (Clause `{clause_no}`).

Under instructions from and on behalf of our Client, **{claimant}**, we hereby serve upon you this Statutory Notice under Section 21 of the Arbitration and Conciliation Act, 1996:

1. **Subsisting Arbitration Agreement:** Our Client and you entered into a written Agreement dated **{contract_date}**, wherein **Clause `{clause_no}`** constitutes a valid and binding arbitration agreement within the meaning of Section 7 of the Arbitration and Conciliation Act, 1996, designating **Bengaluru** as the Seat of Arbitration.
2. **Quantified Claim in Dispute:** On account of breaches and defaults committed from **{default_date}**, an aggregate sum of **INR {claim_amount:,.2f}** (along with pendente lite and future interest at 18 percent per annum under Section 31(7) of the Act) is due and payable by you to our Client.
{core_clause_text}
4. **Invocation under Section 21 & Nomination under Section 11(5):**
   Our Client hereby **invokes arbitration under Section 21** of the Act and proposes that a Retired Judge of the Hon'ble High Court of Karnataka / District Judiciary empanelled with the **Arbitration & Conciliation Centre – Bengaluru (Domestic & International) [ACCB], Khanija Bhavan, Race Course Road, Bengaluru** be appointed as the Sole Arbitrator.
5. You are called upon to communicate your written concurrence within **30 (Thirty) days** from receipt of this Notice, failing which our Client shall immediately file a Civil Miscellaneous Petition (C.M.P.) under **Section 11(6)** before the Hon'ble High Court of Karnataka at Bengaluru at your risk as to costs.

---

## PART III: PETITION FOR INTERIM MEASURES UNDER SECTION 9 (COMMERCIAL COURT, BENGALURU)
**IN THE COURT OF THE LXXXIII ADDITIONAL CITY CIVIL AND SESSIONS JUDGE AT BENGALURU (CCH-84)**
**(DEDICATED COMMERCIAL COURT)**
**COM. A.A. NO. _________ OF 2026**

**IN THE MATTER OF:**
*An Application under Section 9(1)(ii)(b), (d) & (e) of the Arbitration and Conciliation Act, 1996 read with Section 10(3) of the Commercial Courts Act, 2015*

1. **Prima Facie Case & Balance of Convenience:** The Petitioner has an unimpeachable monetary claim of **INR {claim_amount:,.2f}** arising out of the Agreement dated **{contract_date}**.
2. **Risk of Dissipation of Assets (*Essar House Pvt. Ltd. v. Arcellor Mittal Nippon Steel India Ltd.*, 2022 INSC 957):** The Respondent is actively alienating its receivables and encumbering its bank accounts to defeat and obstruct execution of the forthcoming arbitral award. As held by the Hon'ble Supreme Court in *Essar House*, where a strong prima facie case is made out and the balance of convenience tilts in favour of granting interim relief, the Commercial Court under Section 9 exercises wide equitable jurisdiction to secure the amount in dispute without being fettered by technical rigours of Order XXXVIII Rule 5 CPC.
3. **Mandatory Undertaking under Section 9(2):** The Petitioner unconditionally undertakes to ensure that arbitral proceedings are commenced within **90 (Ninety) days** from the date of grant of any interim measure by this Hon'ble Court.

### SECTION 9 PRAYER
WHEREFORE, the Petitioner prays that this Hon'ble Commercial Court may be pleased to:
(a) Direct the Respondent to furnish an unconditional Bank Guarantee or solvent security for **INR {claim_amount:,.2f}** pending culmination of the arbitral proceedings; and
(b) Grant an ad-interim ex-parte order of injunction restraining the Respondent from alienating or encumbering its scheduled assets/receivables to the extent of **INR {claim_amount:,.2f}**.

---

## PART IV: CIVIL MISCELLANEOUS PETITION (C.M.P.) UNDER SECTION 11(6) BEFORE THE HIGH COURT OF KARNATAKA
**IN THE HIGH COURT OF KARNATAKA AT BENGALURU**
**(ORIGINAL ARBITRATION JURISDICTION)**
**CIVIL MISCELLANEOUS PETITION (C.M.P.) NO. _________ OF 2026**

**IN THE MATTER OF:**
*Section 11(6) of the Arbitration and Conciliation Act, 1996*

1. **Existence of Arbitration Agreement under Section 7:** The Agreement dated **{contract_date}** contains an unequivocal arbitration clause at **Clause `{clause_no}`**.
2. **Scope of Referral Court Inquiry (*SBI General Insurance Co. Ltd. v. Krish Spinning*, 2024 INSC 532 & *In Re: Interplay*, 2023 INSC 1066):** In terms of the 7-Judge Constitution Bench decision and *Krish Spinning*, the scrutiny of the Referral Court under Section 11(6) read with Section 11(6A) is strictly confined to a *prima facie* examination of the **existence** of the arbitration agreement, leaving all contentious issues of arbitrability, accord and satisfaction, and stamping to the Arbitral Tribunal under Section 16 (*Kompetenz-Kompetenz*).
3. **Failure of Appointment Procedure:** Despite due service of the statutory Section 21 Notice and expiry of the 30-day statutory period on **{sec11_30d_expiry}**, the Respondent failed to concur on a neutral Sole Arbitrator.

### C.M.P. PRAYER
WHEREFORE, the Petitioner prays that this Hon'ble Court may be pleased to:
(a) Appoint an independent and impartial **Sole Arbitrator** to adjudicate the disputes between the Petitioner and the Respondent arising out of the Agreement dated **{contract_date}** (Clause `{clause_no}`), conducting proceedings at the **Arbitration & Conciliation Centre – Bengaluru (Domestic & International) [ACCB]** in accordance with the Arbitration and Conciliation Centre – Bengaluru Rules, 2012; and
(b) Pass such other order(s) as this Hon'ble Court deems fit in the interest of justice and equity.
"""

    safe_cl = "".join(c if c.isalnum() else "_" for c in clause_no)
    out_path = os.path.join(OUTPUT_DIR, f"arbitration_suite_clause_{safe_cl}_{int(claim_amount)}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(bundle)

    print(bundle)
    print(f"\\n[Success] Arbitration Sec. 21, Sec. 9 & Sec. 11(6) C.M.P. Suite saved -> '{out_path}'")
    return out_path

def handle_arbitration_cli(argv):
    p = argparse.ArgumentParser(prog="sweety legal arbitration")
    p.add_argument("--claimant", default="M/s. Claimant Tech Solutions Pvt. Ltd.")
    p.add_argument("--respondent", default="M/s. Respondent Enterprise Infrastructure Ltd.")
    p.add_argument("--contract-date", required=True, help="Date of contract YYYY-MM-DD")
    p.add_argument("--clause-no", default="18.4", help="Arbitration clause number in contract")
    p.add_argument("--claim-amount", type=float, required=True, help="Quantified claim in INR")
    p.add_argument("--default-date", required=True, help="Date cause of action accrued YYYY-MM-DD")
    p.add_argument("--mutual-clause", action="store_true", help="Set if clause is already mutual (skip CORE 2024 severance)")
    a = p.parse_args(argv)
    generate_arbitration_suite(
        a.claimant, a.respondent, a.contract_date, a.clause_no,
        a.claim_amount, a.default_date, not a.mutual_clause
    )

if __name__ == "__main__":
    if len(sys.argv) > 1:
        handle_arbitration_cli(sys.argv[1:])
'''

# ==============================================================================
# 2. UNIFIED SWEETY.PY ROUTER (ALL 22 MODULES)
# ==============================================================================
UNIFIED_SWEETY_22 = '''# --- SWEETYAI HOME-DIRECTORY SANDBOX ENFORCEMENT ---
from sandbox_guard import activate_home_sandbox as _activate_home_sandbox
_activate_home_sandbox()
# ---------------------------------------------------
# SWEETYAI UNIFIED FAST-PATH ROUTER (22 MODULES)

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

    print("=== SWEETYAI ENTERPRISE LEGAL WORKSTATION (22 MODULES) ===")
    print("Usage: python3 sweety.py legal [review | bail | ni138 | stamp-duty | crl-appeal | ibc | arbitration | sec63-cert | custody-calc | cross-exam | full-audit | docx-redline | claim-xlsx]")

if __name__ == "__main__":
    main()
'''

# ==============================================================================
# 3. UPDATED 22-MODULE MASTER README.MD
# ==============================================================================
README_22 = '''# SWEETYAI ENTERPRISE LEGAL WORKSTATION (INDIA — 22 MODULES)
**A Secure, Air-Gapped, Automated Legal-Tech & Litigation Suite for Indian Legal Professionals**

*Jurisdictions Enforced:* Bharatiya Nyaya Sanhita, 2023 (BNS) | Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) | Bharatiya Sakshya Adhiniyam, 2023 (BSA) | Indian Contract Act, 1872 | Specific Relief Act, 1963 | Arbitration & Conciliation Act, 1996 | Insolvency & Bankruptcy Code, 2016 (IBC) | Negotiable Instruments Act, 1881 | Karnataka Court Fees and Suits Valuation Act, 1958 | Karnataka Stamp Act, 1957 (Act 04 of 2024) | Commercial Courts Act, 2015 | DPDP Act, 2023.

---

## I. SYSTEM SECURITY & SANDBOX ARCHITECTURE
- **Home-Directory Sandbox (`sandbox_guard.py`):** Enforces read, write, and modify permissions strictly inside `/home/madhukumarm`, blocking system root (`/`, `/etc`, `/usr`) writes and path-traversal (`../`) exploits.
- **Privilege Rule:** Never run SweetyAI with `sudo` (`UID 0` execution is blocked).

---

## II. MASTER 22-MODULE CLI QUICK-REFERENCE CARD

| # | Module / Feature Name | CLI Command Syntax | Output Directory | Primary Statutory / Procedural Framework |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Home Sandbox Guard** | Automatic on startup (`sandbox_guard.py`) | Runtime Memory | OS-level isolation to `/home/madhukumarm` |
| **2** | **Anthropic Plugin Sync** | `python3 sweety.py plugin sync` | `anthropic_plugins/` | Anthropic Legal Knowledge-Work SOPs & Prompts |
| **3** | **Clause Redliner & RAG** | `python3 sweety.py legal redline <orig> <mod>` | `redline_outputs/` | Unified clause diff & `parallel` RAG counter-briefs |
| **4** | **6-Pillar Contract Playbook** | `python3 sweety.py legal review <file_or_--latest>` | `contract_review_reports/` | ICA 1872, SRA 1963, A&C Act 1996 (*CORE* 2024), Stamp Act |
| **5** | **Privacy & PII Auditor** | `python3 sweety.py legal privacy-audit <file_or_--latest> --scrub` | `privacy_audit_reports/` | BSA Sec. 132 Privilege, DPDP Act Sec. 8(5), PII Scrubbing |
| **6** | **Citation & Statute Verifier** | `python3 sweety.py legal verify-citations <file_or_--latest>` | `citation_audit_reports/` | Precedent Registry + BNS (1–358) / BNSS (1–531) / BSA (1–170) |
| **7** | **HC Synopsis & List of Dates** | `python3 sweety.py legal chronology <file_or_--latest> --jurisdiction crlp` | `chronology_outputs/` | Karnataka High Court Rules, 1959 + Sec. 173(3) BNSS Delay Audit |
| **8** | **Court Fee & Limitation Calc** | `python3 sweety.py calc-fees --type commercial --value 2500000 --cause-date YYYY-MM-DD` | `valuation_slips/` | Schedule I Art. 1 KCFSV Act, 1958 (16 Slabs) + Limitation Act |
| **9** | **High Court HTML Exporter** | `python3 sweety.py export <file.md>` | `court_ready_exports/` | Ch. XII Rule 2 KHC Rules (A4, Verdana 12pt/14pt, 1.75-in margin) |
| **10** | **Downloads Auto-Scanner** | `python3 sweety.py legal review --list-downloads` | Console Output | Scans `/home/madhukumarm/Downloads` for PDF/DOCX/TXT/MD |
| **11** | **Sec. 63(4) BSA Certifier** | `python3 sweety.py legal sec63-cert <file_or_--latest> --deponent "Name"` | `sec63_certificates/` | Sec. 63(4) & Schedule BSA 2023 (Part A Custodian + Part B SHA-256) |
| **12** | **Sec. 187 BNSS Custody Calc** | `python3 sweety.py legal custody-calc --remand-date YYYY-MM-DD --tier 60` | `custody_bail_reports/` | Sec. 187(2)/(3) BNSS (40/60d PC Window & 60/90d Default Bail) |
| **13** | **Witness Contradiction Matrix** | `python3 sweety.py legal cross-exam <prior> <subsequent> --witness PW-1` | `cross_examination_matrices/` | Sec. 180(3) BNSS + Sec. 148 BSA (*Tahsildar Singh* 2-step protocol) |
| **14** | **Bail Petition Suite** | `python3 sweety.py legal bail --type 482 --forum hc --crime-no "Crime 215/2026"` | `bail_petitions/` | Secs. 480, 482 & 483 BNSS (Anticipatory/Regular Bail + Parokar) |
| **15** | **NI Act Sec. 138 PCR Suite** | `python3 sweety.py legal ni138 --cheque-no 884512 --amount 1500000 ...` | `ni138_complaints/` | Secs. 138, 142, 143A (20% Relief) & Sec. 223 BNSS Complaint |
| **16** | **One-Click Case Packet** | `python3 sweety.py legal full-audit <file_or_--latest> --jurisdiction crlp` | `master_case_dossiers/` | Chains Privacy + Playbook + Citations + Chronology + BSA + HTML |
| **17** | **Native Word `.docx` Redline** | `python3 sweety.py legal docx-redline <orig> <mod>` | `word_docx_exports/` | OpenXML Word Track Changes (`<w:ins>` / `<w:del>`) + KHC Margins |
| **18** | **Formula Excel `.xlsx` Claims** | `python3 sweety.py legal claim-xlsx --principal 2500000 --rate 18 ...` | `excel_claim_schedules/` | Order VII Rule 2A CPC Interest & Specified Value Live Formulas |
| **19** | **Karnataka Stamp Duty & Penalty**| `python3 sweety.py legal stamp-duty --instrument conveyance_urban --value 7500000` | `stamp_duty_reports/` | Karnataka Stamp Act (Act 04 of 2024) + Secs. 33/34 10x Impounding |
| **20** | **Criminal Appeal & Sec. 430 Bail**| `python3 sweety.py legal crl-appeal --cc-no "C.C. 18450/2024" --judgment-date YYYY-MM-DD --fine 1500000` | `criminal_appeals/` | Secs. 415 & 430 BNSS + *Jamboo Bhandari* Sec. 148 NI Act Waiver |
| **21** | **IBC Sec. 8 & Sec. 9 NCLT Suite**| `python3 sweety.py legal ibc --principal 11500000 --rate 18 --default-date YYYY-MM-DD` | `ibc_nclt_petitions/` | Sec. 8 Form 3 Notice + Sec. 9 Form 5 NCLT Petition + Sec. 9(3)(b) |
| **22** | **Arbitration Sec. 21/9/11 Suite**| `python3 sweety.py legal arbitration --contract-date YYYY-MM-DD --claim-amount 4500000 --default-date YYYY-MM-DD` | `arbitration_petitions/` | Sec. 21 Notice (*CORE* 2024) + Sec. 9 Commercial IA + Sec. 11(6) CMP |

---

## III. SHORTCUT FLAGS & MOBILE LAN ACCESS
- **`--latest`**: Automatically targets the newest file in `/home/madhukumarm/Downloads`.
- **`--jurisdiction`**: Presets High Court / Trial formats (`crlp`, `wp`, `rfa`, `comm`).
- **Mobile Browser Bridge:** Run `python3 -m http.server 8080` inside `~/SweetyAI` and open `http://<workstation-ip>:8080` on your phone browser over local Wi-Fi to view and download all generated files.
'''

write_clean("arbitration_engine.py", ARBITRATION_ENGINE_CODE)
write_clean("sweety.py", UNIFIED_SWEETY_22)
write_clean("README.md", README_22)

for fname in ("arbitration_engine.py", "sweety.py"):
    with open(fname, "rb") as f:
        compile(f.read(), fname, "exec")
print("[Compile Check] arbitration_engine.py and sweety.py compiled cleanly with 0 errors!")
print("[Docs Check] README.md updated with all 22 modules!")

print("\n=== [TEST] Running Module 22: Arbitration Sec. 21 Notice, Sec. 9 IA & Sec. 11(6) High Court C.M.P. ===")
subprocess.run([
    "python3", "sweety.py", "legal", "arbitration",
    "--contract-date", "2024-06-15",
    "--clause-no", "19.2",
    "--claim-amount", "4500000",
    "--default-date", "2025-12-01"
], check=True)
