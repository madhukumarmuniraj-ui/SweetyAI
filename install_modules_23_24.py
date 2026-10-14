import os
import sys
import subprocess

def write_clean(filename, content):
    cleaned = content.replace("\u00a0", " ").replace("\u200b", "")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(cleaned)

# ==============================================================================
# 1. MODULE 23: HIGH COURT SEC. 528 BNSS QUASHING & ART. 226/227 WRIT SUITE
# ==============================================================================
HC_QUASH_CODE = '''import os
import sys
import argparse
from datetime import datetime

OUTPUT_DIR = "hc_quashing_petitions"

def generate_hc_quashing_suite(
    petitioner,
    police_station,
    complainant,
    crime_no,
    cc_no,
    trial_court,
    offences,
    fir_date,
    mode="crlp528",
    civil_dispute=True,
    sec175_violation=True
):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if mode == "wp226":
        title_header = (
            "IN THE HIGH COURT OF KARNATAKA AT BENGALURU\\n"
            "(ORIGINAL WRIT JURISDICTION)\\n"
            "WRIT PETITION NO. _________ OF 2026 (GM-RES)"
        )
        provision_line = (
            "Articles 226 and 227 of the Constitution of India read with "
            "Section 528 of the Bharatiya Nagarik Suraksha Sanhita, 2023"
        )
    else:
        title_header = (
            "IN THE HIGH COURT OF KARNATAKA AT BENGALURU\\n"
            "(MEMORANDUM OF CRIMINAL PETITION UNDER SECTION 528 OF THE BHARATIYA NAGARIK SURAKSHA SANHITA, 2023)\\n"
            "CRIMINAL PETITION (CRL.P.) NO. _________ OF 2026"
        )
        provision_line = (
            "Section 528 of the Bharatiya Nagarik Suraksha Sanhita, 2023 "
            "(Corresponding to Section 482 of the Code of Criminal Procedure, 1973)"
        )

    target_proceeding = (
        f"FIR in {crime_no} dated {fir_date} registered by Respondent No. 1 ({police_station}) "
        f"and consequential proceedings in {cc_no} pending on the file of the learned {trial_court}"
        if cc_no != "N/A"
        else f"FIR in {crime_no} dated {fir_date} registered by Respondent No. 1 ({police_station}) pending on the file of the learned {trial_court}"
    )

    extra_grounds = ""
    if civil_dispute:
        extra_grounds += """
3. **Purely Civil / Commercial Dispute Given a Cloak of Criminality (*Indian Oil Corp. v. NEPC India Ltd.*, (2006) 6 SCC 736 & *G. Sagar Suri v. State of U.P.*, (2000) 2 SCC 636):**
   A bare perusal of the complaint and FIR reveals that the gravamen of the dispute arises out of an alleged breach of commercial/contractual obligations. For an offence of cheating under Section 318 BNS (formerly Section 420 IPC), fraudulent or dishonest intention must be shown to exist **at the very inception of the transaction** (*Hridaya Ranjan Prasad Verma v. State of Bihar*, (2000) 4 SCC 168). Mere subsequent failure to keep a commercial promise cannot criminalize a civil dispute, and the criminal justice machinery is being weaponized as an arm-twisting recovery mechanism.
"""
    if sec175_violation:
        extra_grounds += """
4. **Non-Compliance with Mandatory Safeguards under Sections 173(3) & 175(3) BNSS (*Priyanka Srivastava v. State of U.P.*, (2015) 6 SCC 287):**
   The registration of the impugned crime and referral for investigation suffer from incurable procedural illegality. Under **Section 175(3) of the BNSS, 2023**, no Magistrate can mechanically direct registration of an FIR without: (i) verifying prior compliance under Section 173(4) BNSS supported by a sworn affidavit per *Priyanka Srivastava*, (ii) considering the submissions of the Police Officer, and (iii) applying judicial mind via a reasoned speaking order. Furthermore, where the alleged offence carries a punishment between 3 and 7 years, **Section 173(3) BNSS** contemplates a preliminary inquiry to ascertain whether a prima facie case exists.
"""

    bundle = f"""# {title_header}

**IN THE MATTER OF:**
*{provision_line}*

**BETWEEN:**
**{petitioner}**                                                 ... PETITIONER / ACCUSED

**AND:**
1. **The State of Karnataka**
   By `{police_station}`,
   Represented by the State Public Prosecutor,
   High Court Building, Bengaluru - 560 001.

2. **{complainant}**                                             ... RESPONDENTS

---

## PART I: STATUTORY & BHAJAN LAL QUASHING AUDIT MATRIX
| Audit Gate | Controlling Statute / Supreme Court Precedent | Case Applicability |
| :--- | :--- | :--- |
| **Inherent / Writ Jurisdiction** | `{provision_line}` | Invoked to prevent abuse of process of Court & secure ends of justice |
| **Impugned Proceeding** | `{crime_no}` (`{cc_no}`) on the file of `{trial_court}` | Registered on `{fir_date}` under `{offences}` |
| **Bhajan Lal Prong (1) & (3)** | *State of Haryana v. Bhajan Lal*, 1992 Supp (1) SCC 335 | Uncontroverted allegations do not disclose essential ingredients of `{offences}` |
| **Bhajan Lal Prong (7)** | Mala fide & Ulterior Motive | Manifestly attended with mala fides to wreak vengeance / extort settlement |
| **Civil Cloaked as Criminal** | *G. Sagar Suri* (2000) 2 SCC 636; *Lalita Kumari* (2014) 2 SCC 1 | `{'YES — Contractual dispute lacking inception mens rea' if civil_dispute else 'Standard Evidentiary Challenge'}` |
| **Sec. 173(3) / 175(3) BNSS Gate** | *Priyanka Srivastava* (2015) 6 SCC 287 & Sec. 175(3) BNSS | `{'VIOLATED — Mandatory affidavit & police submission inquiry omitted' if sec175_violation else 'Standard FIR Registration Challenge'}` |

---

## PART II: SYNOPSIS & CHRONOLOGICAL LIST OF DATES
*(Prepared under Chapter XII of the High Court of Karnataka Rules, 1959)*

| Sl. No. | Date | Chronological Event |
| :--- | :--- | :--- |
| 1. | Prior to `{fir_date}` | Commercial / civil transactions transpired between the Petitioner and Respondent No. 2 without any dishonest inducement at inception. |
| 2. | `{fir_date}` | Respondent No. 2 lodged a motivated complaint culminating in `{crime_no}` by `{police_station}` for alleged offences under `{offences}`. |
| 3. | Subsequent | `{cc_no}` registered/pending before the learned `{trial_court}`, prompting the present Petition under `{provision_line}`. |

---

## PART III: MEMORANDUM OF PETITION UNDER SECTION 528 BNSS, 2023

The Petitioner above-named most respectfully submits as follows:
1. The Petitioner is approaching this Hon'ble Court invoking its inherent jurisdiction under **{provision_line}**, seeking to quash the **{target_proceeding}** for the alleged offences punishable under **{offences}**.

### GROUNDS FOR QUASHING
1. **Squarely Covered by Parameters (1), (3), (5) and (7) of *State of Haryana v. Bhajan Lal*, 1992 Supp (1) SCC 335:**
   Even if the allegations made in the First Information Report / Complaint are taken at their face value and accepted in their entirety, they do not *prima facie* constitute any offence or make out a case against the Petitioner under **{offences}**.
2. **Absence of Essential Statutory Ingredients (*Mahmood Ali v. State of U.P.*, 2023 INSC 684):**
   As held by the Hon'ble Supreme Court in *Mahmood Ali v. State of U.P.*, while exercising jurisdiction under Section 528 BNSS (formerly Section 482 Cr.P.C.), the High Court has a duty to read between the lines and look beyond clever drafting to see whether the criminal proceeding is manifestly frivolous or vexatious.
{extra_grounds}

### MAIN PRAYER
WHEREFORE, the Petitioner most respectfully prays that this Hon'ble Court may be pleased to:
(a) Call for the relevant records in **{crime_no}** (`{cc_no}`) on the file of the learned **{trial_court}**;
(b) **QUASH** the entire proceedings in **{target_proceeding}** for the offences punishable under **{offences}**, insofar as the Petitioner is concerned; and
(c) Pass such other order or direction as this Hon'ble Court deems fit in the facts and circumstances of the case, in the interest of justice and equity.

---

## PART IV: I.A. NO. 1/2026 FOR INTERIM STAY OF FURTHER PROCEEDINGS
*(Under Section 528 of the Bharatiya Nagarik Suraksha Sanhita, 2023)*

1. For the reasons stated in the accompanying Memorandum of Petition and Affidavit, the continuation of investigation / trial proceedings in **{crime_no}** (`{cc_no}`) operates as a grave abuse of the process of law and infringes the Petitioner's fundamental right to personal liberty under Article 21 of the Constitution.
2. **Compliance with *Neeharika Infrastructure Pvt. Ltd. v. State of Maharashtra*, (2021) 19 SCC 401:** This is an exceptional case where the uncontroverted allegations ex-facie fail to disclose the commission of any cognizable offence, warranting an ad-interim order of stay for reasons recorded.

### INTERIM PRAYER
WHEREFORE, the Petitioner prays that this Hon'ble Court may be pleased to **STAY all further investigation and proceedings** in **{target_proceeding}** pending disposal of the main Petition, in the interest of justice and equity.
"""

    safe_cr = "".join(c if c.isalnum() else "_" for c in crime_no)
    out_path = os.path.join(OUTPUT_DIR, f"hc_quash_{mode}_{safe_cr}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(bundle)

    print(bundle)
    print(f"\\n[Success] High Court Sec. 528 BNSS Quashing / Writ Bundle saved -> '{out_path}'")
    return out_path

def handle_hc_quash_cli(argv):
    p = argparse.ArgumentParser(prog="sweety legal hc-quash")
    p.add_argument("--petitioner", default="Sri. Petitioner / Accused No. 1")
    p.add_argument("--ps", default="Whitefield Police Station, Bengaluru")
    p.add_argument("--complainant", default="Sri. Defacto Complainant")
    p.add_argument("--crime-no", required=True, help="e.g. Crime No. 312/2026")
    p.add_argument("--cc-no", default="C.C. No. 22410/2026", help="Trial Court CC/Spl.C No. or N/A")
    p.add_argument("--trial-court", default="IV Addl. Chief Judicial Magistrate (ACJM), Bengaluru")
    p.add_argument("--offences", default="Sections 316(2) and 318(4) of the Bharatiya Nyaya Sanhita, 2023")
    p.add_argument("--fir-date", required=True, help="YYYY-MM-DD")
    p.add_argument("--mode", choices=["crlp528", "wp226"], default="crlp528", help="crlp528 or wp226")
    p.add_argument("--no-civil", action="store_true", help="Omit civil-dispute ground")
    p.add_argument("--no-175", action="store_true", help="Omit Sec. 173(3)/175(3) BNSS ground")
    a = p.parse_args(argv)
    generate_hc_quashing_suite(
        a.petitioner, a.ps, a.complainant, a.crime_no, a.cc_no,
        a.trial_court, a.offences, a.fir_date, a.mode,
        not a.no_civil, not a.no_175
    )

if __name__ == "__main__":
    if len(sys.argv) > 1:
        handle_hc_quash_cli(sys.argv[1:])
'''

# ==============================================================================
# 2. MODULE 24: COMMERCIAL COURTS ACT SUITE (SEC. 12A PIM, PLAINT & STATEMENT OF TRUTH)
# ==============================================================================
COMM_SUIT_CODE = '''import os
import sys
import argparse
from datetime import datetime

OUTPUT_DIR = "commercial_suits"
CCA_MIN_SPECIFIED_VALUE = 300000.0  # INR 3,00,000 under Sec. 2(1)(i) & Sec. 12 CCA, 2015

def generate_commercial_suit_suite(
    plaintiff,
    defendant,
    principal,
    interest_rate,
    cause_date,
    dispute_clause="Section 2(1)(c)(i) & (xviii) — Sale of Goods / Provision of Services Agreement",
    urgent_interim=False
):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        c_dt = datetime.strptime(cause_date, "%Y-%m-%d")
        days_elapsed = max(0, (datetime.now() - c_dt).days)
    except Exception:
        days_elapsed = 365

    accrued_interest = round(principal * (interest_rate / 100.0) * (days_elapsed / 365.0), 2)
    specified_value = round(principal + accrued_interest, 2)
    meets_cca = specified_value >= CCA_MIN_SPECIFIED_VALUE
    jurisdiction_status = (
        f"MAINTAINABLE BEFORE DEDICATED COMMERCIAL COURT (Specified Value INR {specified_value:,.2f} >= INR 3,00,000 threshold under Sec. 12 CCA)"
        if meets_cca
        else f"BELOW INR 3,00,000 CCA THRESHOLD (File as regular Original Suit O.S. before City Civil Court)"
    )

    sec12a_block = (
        "URGENT INTERIM RELIEF CONTEMPLATED (I.A. under Order XXXVIII Rule 5 / Order XXXIX Rules 1 & 2 CPC) — "
        "Dispensation from Pre-Institution Mediation pleaded under Section 12A(1) read with *Yamini Manohar v. TKD Keerthi*, 2023 INSC 911"
        if urgent_interim
        else "MANDATORY PRE-INSTITUTION MEDIATION (PIM) — Form-1 Application under Rule 3(1) PIMS Rules, 2018 before DLSA, Bengaluru Urban (*Patil Automation v. Rakheja Engineers*, (2022) 10 SCC 1)"
    )

    bundle = f"""# DEDICATED COMMERCIAL COURT LITIGATION SUITE (COMMERCIAL COURTS ACT, 2015)
**(SECTION 12A PIM FORM-1 | COMMERCIAL SUIT PLAINT | ORDER VII RULE 2A SCHEDULE | APPENDIX-I STATEMENT OF TRUTH)**

## PART I: STATUTORY MAINTAINABILITY & SPECIFIED VALUE MATRIX
| Statutory Gate | Provision of Commercial Courts Act, 2015 / CPC | Audit Computation / Verdict |
| :--- | :--- | :--- |
| **Commercial Dispute Category** | `{dispute_clause}` | Falls squarely within **Section 2(1)(c)** of the CCA, 2015 |
| **Principal Claim Amount** | Invoice / Contractual Principal | **INR {principal:,.2f}** |
| **Pre-Suit Interest (Order VII Rule 2A)** | `{interest_rate:.2f} percent p.a.` for `{days_elapsed} days` from `{cause_date}` | **INR {accrued_interest:,.2f}** |
| **SPECIFIED VALUE (Sec. 12 CCA)** | Principal + Pre-Suit Interest up to date of filing | **INR {specified_value:,.2f}** |
| **Pecuniary Threshold Check** | Minimum INR 3,00,000 under Sec. 2(1)(i) CCA | **{jurisdiction_status}** |
| **Section 12A PIM Gate** | *Patil Automation* (2022) 10 SCC 1 / *Yamini Manohar* | **{sec12a_block}** |

---

## PART II: FORM-1 — APPLICATION FOR PRE-INSTITUTION MEDIATION (SECTION 12A CCA)
*[Under Rule 3(1) of the Commercial Courts (Pre-Institution Mediation and Settlement) Rules, 2018]*
**BEFORE THE DISTRICT LEGAL SERVICES AUTHORITY (DLSA), BENGALURU URBAN, CITY CIVIL COURT COMPLEX, BENGALURU**

1. **Name & Address of Applicant (Plaintiff):** `{plaintiff}`, Bengaluru, Karnataka.
2. **Name & Address of Opposite Party (Defendant):** `{defendant}`, Bengaluru, Karnataka.
3. **Category of Commercial Dispute under Section 2(1)(c) CCA, 2015:** `{dispute_clause}`.
4. **Specified Value of Commercial Dispute (Section 12 CCA):** **INR {specified_value:,.2f}** (Principal: INR {principal:,.2f} + Accrued Interest: INR {accrued_interest:,.2f}).
5. **Brief Synopsis of Commercial Dispute:** Despite due performance of contractual obligations by the Applicant, the Opposite Party committed default on **{cause_date}** and failed to liquidate the outstanding principal of **INR {principal:,.2f}**. The Applicant submits this Form-1 Application along with the statutory fee of **INR 1,000/-** seeking issuance of Mediation Notice in Form-2 under Rule 3(2) of the PIMS Rules, 2018.

---

## PART III: COMMERCIAL ORIGINAL SUIT PLAINT (COM. O.S.)
**IN THE COURT OF THE LXXXIII ADDITIONAL CITY CIVIL AND SESSIONS JUDGE AT BENGALURU (CCH-84)**
**(DEDICATED COMMERCIAL COURT AT BENGALURU)**
**COM. O.S. NO. _________ OF 2026**

**BETWEEN:**
**{plaintiff}**                                                  ... PLAINTIFF

**AND:**
**{defendant}**                                                  ... DEFENDANT

### MEMORANDUM OF PLAINT UNDER ORDER VII RULE 1 READ WITH COMMERCIAL COURTS ACT, 2015
1. **Commercial Dispute & Territorial Jurisdiction:** The dispute between the parties arises out of mercantile/commercial transactions covered under **{dispute_clause}** of the Commercial Courts Act, 2015. The cause of action arose at Bengaluru on **{cause_date}**.
2. **Compliance with Section 12A CCA, 2015:** {'The Plaintiff has filed an accompanying I.A. seeking urgent ad-interim relief of attachment before judgment under Order XXXVIII Rule 5 CPC satisfying the parameters in *Yamini Manohar v. TKD Keerthi*, 2023 INSC 911.' if urgent_interim else 'The Plaintiff exhausted mandatory Pre-Institution Mediation before the DLSA, Bengaluru Urban in PIM No. ____/2026, which resulted in a Non-Starter Report in Form-3.'}
3. **Mandatory Interest Pleading under Order VII Rule 2A CPC (Inserted by CCA, 2015):**
   In strict compliance with Order VII Rule 2A of the Code of Civil Procedure, 1908, the Plaintiff sets out the statutory particulars of interest claimed:
   - **(a) Rate at which interest is claimed:** **{interest_rate:.2f} percent per annum** (Commercial contractual / statutory rate under Section 34 CPC Proviso).
   - **(b) Date from which interest is claimed:** **{cause_date}** (Date of commercial default).
   - **(c) Date to which pre-suit interest is calculated:** **{datetime.now().strftime('%Y-%m-%d')}** (`{days_elapsed} days`).
   - **(d) Total amount of pre-suit interest claimed:** **INR {accrued_interest:,.2f}**.
   - **(e) Daily rate at which interest accrues hereafter:** **INR {round((principal * (interest_rate / 100.0)) / 365.0, 2):,.2f} per day**.

### PRAYER IN COMMERCIAL SUIT
WHEREFORE, the Plaintiff prays for a Judgment and Decree against the Defendant:
(a) Directing the Defendant to pay to the Plaintiff the aggregate **Specified Value of INR {specified_value:,.2f}** (comprising Principal of **INR {principal:,.2f}** and Pre-Suit Interest of **INR {accrued_interest:,.2f}**);
(b) Granting *pendente lite* and future interest at **{interest_rate:.2f} percent per annum** on the principal sum of **INR {principal:,.2f}** from the date of institution of the suit until full realization under Section 34 CPC Proviso; and
(c) Awarding realistic commercial costs, advocate fees, and court fees under **Section 35 CPC (as amended by the Commercial Courts Act, 2015)**.

---

## PART IV: APPENDIX-I — STATEMENT OF TRUTH
*[Under First Schedule, Order VI Rule 15A and Order XI Rule 3 of the Code of Civil Procedure, 1908 as amended by the Commercial Courts Act, 2015]*

I, the Authorised Signatory of **{plaintiff}**, do hereby solemnly affirm and declare on oath as under:
1. I am the Authorised Representative of the Plaintiff in the above Commercial Suit and am duly competent to swear this Statement of Truth.
2. I am sufficiently conversant with the facts of the case and have examined all relevant commercial documents and records in relation thereto.
3. I say that the statements made in **Paragraphs 1 to 3** of the Commercial Plaint are true to my personal knowledge and based on commercial records maintained in the ordinary course of business, and legal submissions are believed to be true on legal advice.
4. I say that there is **no false statement or concealment of any material fact, document, or record**, and I have included information that is according to me relevant for the present Commercial Suit.
5. I say that **all documents in my power, possession, control, or custody** pertaining to the facts and circumstances of the proceedings initiated by me have been disclosed and copies thereof annexed with the Plaint, and that I do not have any other documents in my power, possession, control, or custody.
6. I am aware that if any part of this Statement is found to be false, I shall be liable for action under the Bharatiya Nyaya Sanhita, 2023 and the Code of Civil Procedure, 1908.
"""

    out_path = os.path.join(OUTPUT_DIR, f"comm_suit_sec12A_{int(principal)}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(bundle)

    print(bundle)
    print(f"\\n[Success] Commercial Suit, Sec. 12A PIM & Statement of Truth saved -> '{out_path}'")
    return out_path

def handle_comm_suit_cli(argv):
    p = argparse.ArgumentParser(prog="sweety legal comm-suit")
    p.add_argument("--plaintiff", default="M/s. Plaintiff Commercial Enterprises Pvt. Ltd.")
    p.add_argument("--defendant", default="M/s. Defendant Logistics & Infra Pvt. Ltd.")
    p.add_argument("--principal", type=float, required=True, help="Principal claim amount in INR")
    p.add_argument("--rate", type=float, default=18.0, help="Commercial interest rate in percent per annum")
    p.add_argument("--cause-date", required=True, help="Date of commercial default YYYY-MM-DD")
    p.add_argument("--urgent-interim", action="store_true", help="Plead Sec. 12A dispensation via Yamini Manohar urgent relief")
    a = p.parse_args(argv)
    generate_commercial_suit_suite(
        a.plaintiff, a.defendant, a.principal, a.rate, a.cause_date,
        urgent_interim=a.urgent_interim
    )

if __name__ == "__main__":
    if len(sys.argv) > 1:
        handle_comm_suit_cli(sys.argv[1:])
'''

# ==============================================================================
# 3. UNIFIED SWEETY.PY ROUTER (ALL 24 MODULES)
# ==============================================================================
UNIFIED_SWEETY_24 = '''# --- SWEETYAI HOME-DIRECTORY SANDBOX ENFORCEMENT ---
from sandbox_guard import activate_home_sandbox as _activate_home_sandbox
_activate_home_sandbox()
# ---------------------------------------------------
# SWEETYAI UNIFIED FAST-PATH ROUTER (24 MODULES)

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

    print("=== SWEETYAI ENTERPRISE LEGAL WORKSTATION (24 MODULES) ===")
    print("Usage: python3 sweety.py legal [review | bail | ni138 | stamp-duty | crl-appeal | ibc | arbitration | hc-quash | comm-suit | sec63-cert | custody-calc | cross-exam | full-audit | docx-redline | claim-xlsx]")

if __name__ == "__main__":
    main()
'''

write_clean("hc_quashing_writ_engine.py", HC_QUASH_CODE)
write_clean("commercial_suit_engine.py", COMM_SUIT_CODE)
write_clean("sweety.py", UNIFIED_SWEETY_24)

for fname in ("hc_quashing_writ_engine.py", "commercial_suit_engine.py", "sweety.py"):
    with open(fname, "rb") as f:
        compile(f.read(), fname, "exec")
print("[Compile Check] hc_quashing_writ_engine.py, commercial_suit_engine.py, and sweety.py compiled with 0 errors!")

print("\n=== [TEST 1] Module 23: High Court Sec. 528 BNSS Quashing Petition (Bhajan Lal + Sec. 175(3) BNSS) ===")
subprocess.run([
    "python3", "sweety.py", "legal", "hc-quash",
    "--crime-no", "Crime No. 312/2026",
    "--fir-date", "2026-08-14",
    "--mode", "crlp528"
], check=True)

print("\n=== [TEST 2] Module 24: Commercial Courts Act Sec. 12A PIM, Plaint & Statement of Truth ===")
subprocess.run([
    "python3", "sweety.py", "legal", "comm-suit",
    "--principal", "3800000",
    "--rate", "18",
    "--cause-date", "2025-10-01"
], check=True)
