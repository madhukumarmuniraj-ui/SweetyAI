import os
import sys
import subprocess

def write_clean(filename, content):
    cleaned = content.replace("\u00a0", " ")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(cleaned)

# ==============================================================================
# 1. MODULE 20: CRIMINAL APPEAL & SEC. 430 BNSS SUSPENSION OF SENTENCE ENGINE
# ==============================================================================
CRL_APPEAL_CODE = '''import os
import sys
import argparse
from datetime import datetime, timedelta

OUTPUT_DIR = "criminal_appeals"

def generate_criminal_appeal(
    appellant,
    respondent,
    trial_court,
    cc_no,
    judgment_date,
    offence,
    sentence_months,
    fine_amount,
    forum="sessions",
    waive_148=True
):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Limitation check (30 days to Sessions Court, 60 days to High Court under Art. 115 Limitation Act)
    lim_days = 60 if forum == "hc" else 30
    try:
        j_dt = datetime.strptime(judgment_date, "%Y-%m-%d")
        due_dt = j_dt + timedelta(days=lim_days)
        days_elapsed = (datetime.now() - j_dt).days
        lim_status = (
            f"WITHIN LIMITATION ({days_elapsed}/{lim_days} days elapsed; Last Date: {due_dt.strftime('%d.%m.%Y')})"
            if days_elapsed <= lim_days
            else f"DELAY OF {days_elapsed - lim_days} DAYS (Requires I.A. under Sec. 5 Limitation Act, 1963)"
        )
    except Exception:
        lim_status = "Check Certified Copy exclusion under Sec. 12(2) Limitation Act, 1963"

    forum_header = (
        "IN THE HIGH COURT OF KARNATAKA AT BENGALURU\\n(APPELLATE JURISDICTION)\\nCRIMINAL APPEAL NO. _________ OF 2026"
        if forum == "hc"
        else "IN THE COURT OF THE PRINCIPAL CITY CIVIL AND SESSIONS JUDGE AT BENGALURU (CCH-1)\\nCRIMINAL APPEAL NO. _________ OF 2026"
    )
    appeal_sec = "Section 415(2) of the Bharatiya Nagarik Suraksha Sanhita, 2023" if forum == "hc" else "Section 415(3) of the Bharatiya Nagarik Suraksha Sanhita, 2023"
    deposit_20_pct = fine_amount * 0.20

    waiver_clause = ""
    if waive_148:
        waiver_clause = f"""
### SPECIFIC GROUNDS FOR WAIVER / REDUCTION OF 20% DEPOSIT UNDER SECTION 148 NI ACT:
1. **Ratio in Jamboo Bhandari v. M.P. SIDC Ltd., (2023) 10 SCC 446 & Muskan Enterprises v. State of Punjab, 2024 INSC 1046:** The Hon'ble Supreme Court has authoritatively held that directing a 20% deposit under Section 148 of the NI Act is **not an absolute or mechanical rule**. Where the Appellate Court is satisfied that imposing the condition of 20% deposit (**INR {deposit_20_pct:,.2f}**) would be unjust or deprive the Appellant of his statutory right of appeal and personal liberty under Article 21 of the Constitution, the Court has the discretion to waive or reduce the deposit for reasons recorded in writing.
2. **Prima Facie Perversity in Impugned Judgment:** The Trial Court failed to appreciate material contradictions elicited during cross-examination under Section 148 BSA, 2023, rendering the conviction ex-facie unsustainable.
"""

    bundle = f"""# {forum_header}

**IN THE MATTER OF:**
*{appeal_sec} (Corresponding to Section 374 Cr.P.C.)*

**BETWEEN:**
**{appellant}**                                                  ... APPELLANT / ACCUSED

**AND:**
**{respondent}**                                                 ... RESPONDENT / COMPLAINANT

---

## PART I: STATUTORY LIMITATION & SENTENCE AUDIT
| Audit Parameter | Computation / Detail |
| :--- | :--- |
| **Impugned Case & Court** | `{cc_no}` passed by `{trial_court}` |
| **Date of Conviction Judgment** | `{judgment_date}` |
| **Offence Convicted Under** | `{offence}` |
| **Substantive Sentence Imposed** | `{sentence_months} Months Simple Imprisonment` |
| **Fine / Compensation Awarded** | **INR {fine_amount:,.2f}** |
| **20% Appellate Deposit (Sec. 148 NI Act)** | **INR {deposit_20_pct:,.2f}** (`{'Waiver / Reduction Sought' if waive_148 else 'Standard 20% Deposit'}`) |
| **Limitation Audit (Art. 115 Limitation Act)** | **{lim_status}** |

---

## PART II: MEMORANDUM OF CRIMINAL APPEAL UNDER {appeal_sec.upper()}

The Appellant above-named respectfully submits as follows:
1. Being aggrieved by the impugned Judgment of Conviction and Order of Sentence dated **{judgment_date}** passed in **{cc_no}** by the learned **{trial_court}**, convicting the Appellant for the offence punishable under **{offence}** and sentencing him to undergo **{sentence_months} months** imprisonment and pay compensation/fine of **INR {fine_amount:,.2f}**, the Appellant prefers this statutory first appeal.

### GROUNDS OF APPEAL
1. **Impugned Judgment Contrary to Law and Evidence:** That the impugned judgment of conviction is perverse, arbitrary, and contrary to the weight of ocular and documentary evidence on record.
2. **Failure to Prove Foundational Facts Beyond Reasonable Doubt:** The learned Trial Court gravely erred in drawing statutory presumptions without the Respondent first discharging the initial evidentiary burden under the Bharatiya Sakshya Adhiniyam, 2023.
3. **Improper Appreciation of Defence Probable Preponderance:** It is trite law (*Basalingappa v. Mudibasappa*, (2019) 5 SCC 418) that an accused need only raise a probable defence on a preponderance of probabilities, which the Appellant squarely established through cross-examination.
4. **Non-Compliance with Section 351 BNSS (Sec. 313 Cr.P.C.):** Incriminating circumstances were not specifically and individually put to the Appellant during his examination under Section 351 BNSS, causing grave prejudice.

### PRAYER IN MAIN APPEAL
WHEREFORE, the Appellant prays that this Hon'ble Court may be pleased to:
(a) Call for the Trial Court Records in **{cc_no}** on the file of the learned **{trial_court}**;
(b) Set aside the impugned Judgment of Conviction and Order of Sentence dated **{judgment_date}** in **{cc_no}**, and acquit the Appellant of all charges; and
(c) Pass such other order(s) as deemed fit in the interest of justice and equity.

---

## PART III: I.A. NO. 1/2026 UNDER SECTION 430(1) BNSS FOR SUSPENSION OF SENTENCE & BAIL

**APPLICATION UNDER SECTION 430(1) OF THE BHARATIYA NAGARIK SURAKSHA SANHITA, 2023 (FORMERLY SECTION 389(1) CR.P.C.) READ WITH SECTION 148 OF THE NI ACT, 1881**

1. The Appellant has a strong prima facie case on merits in the accompanying Criminal Appeal and every likelihood of succeeding before this Hon'ble Appellate Court.
2. **Fixed-Term Sentence Liberal Standard (*Bhagwan Rama Shinde Gosai v. State of Gujarat*, (1999) 4 SCC 421):** As the substantive sentence imposed is a short fixed term of **{sentence_months} months**, refusal to suspend the sentence pending disposal of the appeal would render the statutory right of appeal infructuous.
3. The Appellant was on bail throughout the trial before the learned Trial Court and never misused the liberty granted to him.
{waiver_clause}
### INTERIM PRAYER
WHEREFORE, the Appellant prays that this Hon'ble Court may be pleased to **SUSPEND the operation and execution of the substantive sentence of imprisonment and fine/compensation** passed in **{cc_no}** dated **{judgment_date}** by the learned **{trial_court}**, enlarge the Appellant on bail, and {'dispense with / reduce the condition of 20% deposit under Section 148 of the NI Act in view of *Jamboo Bhandari* (2023) 10 SCC 446' if waive_148 else 'grant 60 days time to deposit 20% compensation'}, pending disposal of the above Criminal Appeal, in the interest of justice.
"""

    safe_cc = "".join(c if c.isalnum() else "_" for c in cc_no)
    out_path = os.path.join(OUTPUT_DIR, f"crl_appeal_sec415_430_{safe_cc}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(bundle)

    print(bundle)
    print(f"\\n[Success] Criminal Appeal & Sec. 430 BNSS Suspension Bundle saved -> '{out_path}'")
    return out_path

def handle_crl_appeal_cli(argv):
    p = argparse.ArgumentParser(prog="sweety legal crl-appeal")
    p.add_argument("--appellant", default="Sri. Accused / Appellant")
    p.add_argument("--respondent", default="M/s. Complainant / State of Karnataka")
    p.add_argument("--trial-court", default="XXVI ACMM / JMFC, Bengaluru")
    p.add_argument("--cc-no", required=True, help="Trial Court Case No., e.g. C.C. No. 14205/2024")
    p.add_argument("--judgment-date", required=True, help="YYYY-MM-DD")
    p.add_argument("--offence", default="Section 138 of the Negotiable Instruments Act, 1881")
    p.add_argument("--sentence-months", type=int, default=6)
    p.add_argument("--fine", type=float, required=True, help="Total fine or compensation awarded in INR")
    p.add_argument("--forum", choices=["sessions", "hc"], default="sessions")
    p.add_argument("--no-waiver", action="store_true", help="Disable Jamboo Bhandari 20%% waiver ground")
    a = p.parse_args(argv)
    generate_criminal_appeal(
        a.appellant, a.respondent, a.trial_court, a.cc_no,
        a.judgment_date, a.offence, a.sentence_months, a.fine,
        a.forum, not a.no_waiver
    )

if __name__ == "__main__":
    if len(sys.argv) > 1:
        handle_crl_appeal_cli(sys.argv[1:])
'''

# ==============================================================================
# 2. MODULE 21: NCLT / IBC SECTION 8 & 9 OPERATIONAL CREDITOR SUITE
# ==============================================================================
IBC_ENGINE_CODE = '''import os
import sys
import argparse
from datetime import datetime, timedelta

OUTPUT_DIR = "ibc_nclt_petitions"
IBC_SEC4_THRESHOLD = 10000000.0  # INR 1 Crore under Sec. 4 IBC (Notification S.O. 1205(E))

def generate_ibc_suite(
    operational_creditor,
    corporate_debtor,
    cin,
    principal,
    interest_rate,
    default_date,
    invoice_no
):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    try:
        def_dt = datetime.strptime(default_date, "%Y-%m-%d")
        days_default = max(0, (datetime.now() - def_dt).days)
        lim_expiry = def_dt + timedelta(days=365 * 3)
        lim_ok = datetime.now() <= lim_expiry
        lim_text = (
            f"VALID under Art. 137 Limitation Act, 1963 (3-Year Expiry: {lim_expiry.strftime('%d.%m.%Y')})"
            if lim_ok else f"TIME-BARRED under Art. 137 unless Sec. 18 Balance Sheet / Part-Payment acknowledgment exists"
        )
    except Exception:
        days_default = 365
        lim_text = "Verify 3-Year Period under Art. 137 Limitation Act (*B.K. Educational Services*)"

    accrued_interest = round(principal * (interest_rate / 100.0) * (days_default / 365.0), 2)
    total_debt = round(principal + accrued_interest, 2)
    meets_sec4 = total_debt >= IBC_SEC4_THRESHOLD
    sec4_status = (
        f"MAINTAINABLE BEFORE NCLT (Exceeds INR 1,00,00,000 threshold under Sec. 4 IBC by INR {total_debt - IBC_SEC4_THRESHOLD:,.2f})"
        if meets_sec4
        else f"BELOW SEC. 4 IBC THRESHOLD (Short by INR {IBC_SEC4_THRESHOLD - total_debt:,.2f} — File Commercial Summary Suit / MSME Samadhaan instead)"
    )

    bundle = f"""# BEFORE THE NATIONAL COMPANY LAW TRIBUNAL, BENGALURU BENCH
**(CORPORATE INSOLVENCY RESOLUTION PROCESS UNDER SECTIONS 8 & 9 OF THE IBC, 2016)**

## PART I: STATUTORY MAINTAINABILITY & DEFAULT COMPUTATION LEDGER
| Statutory Gate | Legal Standard / Provision | Computed Value / Verdict |
| :--- | :--- | :--- |
| **Operational Creditor** | Section 5(20) IBC, 2016 | **{operational_creditor}** |
| **Corporate Debtor & CIN** | Section 3(8) IBC, 2016 | **{corporate_debtor}** (`CIN: {cin}`) |
| **Unpaid Invoice Reference** | Rule 5 AAA Rules, 2016 | `{invoice_no}` (Date of Default: `{default_date}`) |
| **Principal Operational Debt** | Section 5(21) IBC, 2016 | **INR {principal:,.2f}** |
| **Accrued Contractual Interest** | `{interest_rate:.2f}% p.a.` for `{days_default} days` | **INR {accrued_interest:,.2f}** |
| **TOTAL AMOUNT IN DEFAULT** | Principal + Interest | **INR {total_debt:,.2f}** |
| **Section 4 IBC Threshold Gate** | Min. **INR 1,00,00,000** (S.O. 1205(E)) | **{sec4_status}** |
| **Limitation Audit (Art. 137)** | *B.K. Educational Services v. Parag Gupta* | **{lim_text}** |

---

## PART II: FORM 3 — STATUTORY DEMAND NOTICE UNDER SECTION 8(1) IBC, 2016
*[Under Rule 5 of the Insolvency and Bankruptcy (Application to Adjudicating Authority) Rules, 2016]*

**To:**
The Board of Directors,
**{corporate_debtor}** (CIN: `{cin}`)
Registered Office: Bengaluru, Karnataka.

**Subject:** Demand Notice demanding payment in respect of unpaid operational debt due from **{corporate_debtor}** under the Insolvency and Bankruptcy Code, 2016.

Madam / Sir,
1. **Particulars of Unpaid Operational Debt:**
   - **Total Amount of Debt:** **INR {total_debt:,.2f}** (Principal: INR {principal:,.2f} + Interest @ {interest_rate:.2f}% p.a.: INR {accrued_interest:,.2f}).
   - **Date of Default:** **{default_date}** (Invoice Ref: `{invoice_no}`).
2. **Statutory 10-Day Notice under Section 8(2) IBC:**
   You are hereby unconditionally called upon to unconditionally pay the unpaid operational debt of **INR {total_debt:,.2f}** within **10 (Ten) days** from the receipt of this Demand Notice, or bring to the notice of the undersigned the existence of any genuine **pre-existing dispute** (prior to receipt of this notice as mandated in *Mobilox Innovations Pvt. Ltd. v. Kirusa Software Pvt. Ltd.*, (2018) 1 SCC 353) or record of repayment, failing which Corporate Insolvency Resolution Process (CIRP) proceedings under **Section 9 of the IBC, 2016** shall be initiated before the Hon'ble NCLT, Bengaluru Bench.

---

## PART III: FORM 5 — APPLICATION BY OPERATIONAL CREDITOR UNDER SECTION 9 IBC, 2016
*[Under Rule 6 of the Insolvency and Bankruptcy (Application to Adjudicating Authority) Rules, 2016]*

- **Part I (Applicant):** `{operational_creditor}`
- **Part II (Corporate Debtor):** `{corporate_debtor}` (`CIN: {cin}`), having Nominal/Paid-up Capital exceeding statutory norms and Registered Office within the territorial jurisdiction of NCLT Bengaluru Bench.
- **Part III (Proposed IRP):** *(To be nominated or appointed by the Hon'ble Adjudicating Authority from the IBBI Panel under Section 16(3)(a) IBC).*
- **Part IV (Particulars of Operational Debt):**
  1. Total Amount of Operational Debt Claimed: **INR {total_debt:,.2f}**
  2. Date on which Default Occurred: **{default_date}**
  3. Record of Default with Information Utility (NeSL Form C): *Enclosed as Annexure-A5*.
- **Part V (Particulars of Operational Debt Documents, Records & Evidence of Default):**
  1. Copy of Purchase Order & Tax Invoice `{invoice_no}` (*Annexure-A1*).
  2. Copy of Section 8(1) Form 3 Demand Notice with RPAD & Email Delivery Proof (*Annexure-A2*).
  3. Copy of Ledger Account maintained by the Operational Creditor (*Annexure-A3*).
  4. Certificate / Bank Statement confirming non-receipt of unpaid operational debt under Section 9(3)(c) IBC (*Annexure-A4*).

---

## PART IV: MANDATORY AFFIDAVIT UNDER SECTION 9(3)(b) OF THE IBC, 2016

I, Authorised Signatory of **{operational_creditor}**, do hereby solemnly affirm and state on oath as follows:
1. That the Operational Creditor served the statutory Demand Notice in Form 3 under Section 8(1) of the IBC, 2016 upon the Corporate Debtor **{corporate_debtor}**.
2. That notwithstanding the expiry of the statutory period of **10 (Ten) days** from the date of delivery of the Demand Notice, the Operational Creditor has **neither received payment** of the unpaid operational debt of **INR {total_debt:,.2f}** **nor received any notice of a genuine pre-existing dispute** from the Corporate Debtor under Section 8(2) of the Code.
"""

    safe_inv = "".join(c if c.isalnum() else "_" for c in invoice_no)
    out_path = os.path.join(OUTPUT_DIR, f"ibc_sec8_sec9_{safe_inv}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(bundle)

    print(bundle)
    print(f"\\n[Success] IBC Section 8 Form 3 & Section 9 Form 5 NCLT Bundle saved -> '{out_path}'")
    return out_path

def handle_ibc_cli(argv):
    p = argparse.ArgumentParser(prog="sweety legal ibc")
    p.add_argument("--creditor", default="M/s. Operational Creditor Pvt. Ltd.")
    p.add_argument("--debtor", default="M/s. Defaulting Corporate Debtor Infra Ltd.")
    p.add_argument("--cin", default="U72200KA2018PTC114209")
    p.add_argument("--principal", type=float, required=True, help="Unpaid invoice principal in INR")
    p.add_argument("--rate", type=float, default=18.0, help="Contractual interest rate %% p.a.")
    p.add_argument("--default-date", required=True, help="Date of default YYYY-MM-DD")
    p.add_argument("--invoice-no", default="INV/BLR/2025-26/089")
    a = p.parse_args(argv)
    generate_ibc_suite(a.creditor, a.debtor, a.cin, a.principal, a.rate, a.default_date, a.invoice_no)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        handle_ibc_cli(sys.argv[1:])
'''

# ==============================================================================
# 3. UNIFIED SWEETY.PY ROUTER (ALL 21 MODULES CLEANLY WIRED)
# ==============================================================================
UNIFIED_SWEETY = '''# --- SWEETYAI HOME-DIRECTORY SANDBOX ENFORCEMENT ---
from sandbox_guard import activate_home_sandbox as _activate_home_sandbox
_activate_home_sandbox()
# ---------------------------------------------------
# SWEETYAI UNIFIED FAST-PATH ROUTER (21 MODULES)

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

    print("=== SWEETYAI ENTERPRISE LEGAL WORKSTATION (21 MODULES) ===")
    print("Usage: python3 sweety.py legal [review | bail | ni138 | stamp-duty | crl-appeal | ibc | sec63-cert | custody-calc | cross-exam | full-audit | docx-redline | claim-xlsx]")

if __name__ == "__main__":
    main()
'''

write_clean("crl_appeal_engine.py", CRL_APPEAL_CODE)
write_clean("ibc_engine.py", IBC_ENGINE_CODE)
write_clean("sweety.py", UNIFIED_SWEETY)

for fname in ("crl_appeal_engine.py", "ibc_engine.py", "sweety.py"):
    with open(fname, "rb") as f:
        compile(f.read(), fname, "exec")
print("[Compile Check] crl_appeal_engine.py, ibc_engine.py, and sweety.py compiled with 0 errors!")

print("\n=== [TEST 1] Module 20: Criminal Appeal & Sec. 430 BNSS Suspension of Sentence ===")
subprocess.run([
    "python3", "sweety.py", "legal", "crl-appeal",
    "--cc-no", "C.C. No. 18450/2024",
    "--judgment-date", "2026-09-25",
    "--fine", "1500000",
    "--sentence-months", "6",
    "--forum", "sessions"
], check=True)

print("\n=== [TEST 2] Module 21: IBC Sec. 8 Demand Notice (Form 3) & Sec. 9 NCLT Petition (Form 5) ===")
subprocess.run([
    "python3", "sweety.py", "legal", "ibc",
    "--principal", "11500000",
    "--rate", "18",
    "--default-date", "2025-11-10",
    "--invoice-no", "INV-BLR-2025-904"
], check=True)
