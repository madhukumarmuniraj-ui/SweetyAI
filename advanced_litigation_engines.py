import os
import sys
import argparse
from datetime import datetime

def _safe_name(name):
    return "".join(c if c.isalnum() else "_" for c in name)

# --- MODULE 33: IBC SECTION 7 & 10 FINANCIAL CREDITOR / CORPORATE APPLICANT SUITE ---
def generate_ibc_sec7_petition(financial_creditor, corporate_debtor, default_amount, default_date):
    os.makedirs("ibc_sec7_petitions", exist_ok=True)
    safe_name = _safe_name(corporate_debtor)
    path = f"ibc_sec7_petitions/ibc_sec7_{safe_name}.md"
    content = f"""# BEFORE THE NATIONAL COMPANY LAW TRIBUNAL (NCLT), BENGALURU BENCH
C.P. (IB) NO. _________ OF 2026

**IN THE MATTER OF THE INSOLVENCY AND BANKRUPTCY CODE, 2016**
**AND IN THE MATTER OF:**
**{financial_creditor}**                                          ... FINANCIAL CREDITOR / APPLICANT
**VERSUS**
**{corporate_debtor}**                                            ... CORPORATE DEBTOR

---
## APPLICATION UNDER SECTION 7 OF THE INSOLVENCY AND BANKRUPTCY CODE, 2016
1. **Particulars of Financial Debt:** Total default amounting to **INR {default_amount:,.2f}** arising out of term loan / credit facilities.
2. **Date of Default:** Default occurred and crystallized on **{default_date}**, supported by records of default from Information Utility (NeSL) and bank statement entries.
3. **Proposed Insolvency Professional:** Name of proposed IRP: Sri. ___________________, Reg. No. IBBI/IPA-___/IP-_____/2025-26/_____
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Success] IBC Sec. 7 Petition saved -> '{path}'")

# --- MODULE 34: CONSTITUTIONAL WRIT & PIL SUITE (ARTICLE 226) ---
def generate_writ_petition(petitioner, respondents, grievance_subject):
    os.makedirs("writ_petitions", exist_ok=True)
    safe_name = _safe_name(petitioner)
    path = f"writ_petitions/writ_petition_{safe_name}.md"
    content = f"""# IN THE HIGH COURT OF KARNATAKA AT BENGALURU
WRIT PETITION NO. _________ OF 2026 (GM-RES)

**BETWEEN:**
**{petitioner}**                                                  ... PETITIONER
**AND:**
**{respondents}**                                                 ... RESPONDENTS

---
## WRIT PETITION UNDER ARTICLES 226 & 227 OF THE CONSTITUTION OF INDIA
1. **Nature of Impugned Action / Inaction:** The Petitioner approaches this Hon'ble Court challenging the arbitrary and illegal administrative action regarding: `{grievance_subject}`.
2. **Violation of Fundamental Rights:** The action violates Articles 14, 19(1)(g), and 21 of the Constitution of India and principles of natural justice without statutory authority.
3. **Interim Prayer:** Stay of operation of impugned notice / executive order pending disposal of writ petition.
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Success] Writ Petition saved -> '{path}'")

# --- MODULE 35: CYBER LAW & IT ACT SUITE ---
def generate_cyber_notice(complainant, target_entity, breach_nature):
    os.makedirs("cyber_notices", exist_ok=True)
    safe_name = _safe_name(complainant)
    path = f"cyber_notices/cyber_notice_{safe_name}.md"
    content = f"""# LEGAL NOTICE UNDER THE INFORMATION TECHNOLOGY ACT, 2000

**FROM:** Counsel for **{complainant}**
**TO:** **{target_entity}**

1. **Nature of Cyber Violation:** Unlawful interception, data theft, identity assumption, and computer resource tampering under **Sections 66, 66C, and 79 of the Information Technology Act, 2000**.
2. **Details of Incident:** `{breach_nature}`.
3. **Demand:** Immediate removal/takedown of unauthorized data, preservation of server logs, and payment of damages within **48 hours**, failing which criminal cybercrime complaint and civil suit for compensation will be initiated.
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Success] Cyber Notice saved -> '{path}'")

# --- MODULE 36: RERA ACT, 2016 COMPLAINT SUITE ---
def generate_rera_complaint(allottee, promoter, project_name, delay_months, refund_amount):
    os.makedirs("rera_petitions", exist_ok=True)
    safe_name = _safe_name(allottee)
    path = f"rera_petitions/rera_complaint_{safe_name}.md"
    content = f"""# BEFORE THE KARNATAKA REAL ESTATE REGULATORY AUTHORITY (K-RERA)
COMPLAINT NO. _________ OF 2026

**BETWEEN:**
**{allottee}**                                                    ... ALLOTTEE / COMPLAINANT
**AND:**
**{promoter}**                                                    ... PROMOTER / BUILDER

---
## COMPLAINT UNDER SECTION 31 READ WITH SECTION 18 OF THE RERA ACT, 2016
1. **Project Details:** Booking in project titled **"{project_name}"** registered under K-RERA Reg. No. ___________________
2. **Delayed Possession & Default:** Builder failed to hand over possession within the agreed contractual deadline, causing a continuous delay of `{delay_months} months`.
3. **Relief Claimed under Section 18:** Full refund of principal amount of **INR {refund_amount:,.2f}** along with prescribed interest rate plus MCLR and compensation for mental agony.
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Success] RERA Complaint saved -> '{path}'")

def handle_ibc_sec7_cli(args):
    p = argparse.ArgumentParser(prog="sweety legal ibc-sec7")
    p.add_argument("--creditor", default="State Bank of India")
    p.add_argument("--debtor", default="M/s. Innovate Infrastructure Ltd.")
    p.add_argument("--amount", type=float, default=25000000.0)
    p.add_argument("--date", default="2025-10-15")
    a = p.parse_args(args)
    generate_ibc_sec7_petition(a.creditor, a.debtor, a.amount, a.date)

def handle_writ_cli(args):
    p = argparse.ArgumentParser(prog="sweety legal writ")
    p.add_argument("--petitioner", default="Sri. Harish Gowda")
    p.add_argument("--respondents", default="State of Karnataka & Others")
    p.add_argument("--subject", default="Arbitrary withholding of statutory license and building approval.")
    a = p.parse_args(args)
    generate_writ_petition(a.petitioner, a.respondents, a.subject)

def handle_cyber_cli(args):
    p = argparse.ArgumentParser(prog="sweety legal cyber")
    p.add_argument("--complainant", default="Smt. Deepa Ramesh")
    p.add_argument("--target", default="M/s. WebScrape Cyber Tech")
    p.add_argument("--breach", default="Unauthorized data scraping, breach of PII, and identity spoofing.")
    a = p.parse_args(args)
    generate_cyber_notice(a.complainant, a.target, a.breach)

def handle_rera_cli(args):
    p = argparse.ArgumentParser(prog="sweety legal rera")
    p.add_argument("--allottee", default="Sri. Naveen Kumar")
    p.add_argument("--promoter", default="M/s. Prestige Skylines Builders")
    p.add_argument("--project", default="Prestige Grandeur Apartments")
    p.add_argument("--months", type=int, default=18)
    p.add_argument("--amount", type=float, default=6500000.0)
    a = p.parse_args(args)
    generate_rera_complaint(a.allottee, a.promoter, a.project, a.months, a.amount)
