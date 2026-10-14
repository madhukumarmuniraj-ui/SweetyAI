import os
import sys
import argparse
from datetime import datetime

def _safe_name(name):
    return "".join(c if c.isalnum() else "_" for c in name)

# --- MODULE 29: CONSUMER PROTECTION SUITE ---
def generate_consumer_complaint(complainant, opposite_party, defect_desc, compensation_claimed):
    os.makedirs("consumer_petitions", exist_ok=True)
    safe_comp = _safe_name(complainant)
    path = f"consumer_petitions/consumer_complaint_{safe_comp}.md"
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
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Success] Consumer Complaint saved -> '{path}'")

# --- MODULE 30: MACT COMPENSATION SUITE ---
def generate_mact_petition(claimant, insurer, accident_date, compensation_amount):
    os.makedirs("mact_petitions", exist_ok=True)
    safe_claim = _safe_name(claimant)
    path = f"mact_petitions/mact_claim_{safe_claim}.md"
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
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Success] MACT Petition saved -> '{path}'")

# --- MODULE 31: IPR & TRADEMARK SUITE ---
def generate_ipr_notice(brand_owner, infringer, trademark_name):
    os.makedirs("ipr_notices", exist_ok=True)
    safe_owner = _safe_name(brand_owner)
    path = f"ipr_notices/ipr_cease_desist_{safe_owner}.md"
    content = f"""# CEASE & DESIST LEGAL NOTICE (TRADEMARKS ACT, 1999)

**FROM:** Counsel for **{brand_owner}** (Registered Proprietor)
**TO:** **{infringer}**

1. **Proprietary Rights:** Our client is the registered owner of the trademark **"{trademark_name}"** under Class ___ of the Trademarks Act, 1999.
2. **Infringement:** It has come to our notice that you are unauthorizedly using a deceptively similar mark in the course of trade, causing consumer confusion and passing off.
3. **Demand:** Cease all usage, surrender infringing stock, and tender unconditional written apology within **48 hours**, failing which civil suit for permanent injunction and damages will be instituted.
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Success] IPR Notice saved -> '{path}'")

# --- MODULE 32: LABOUR & INDUSTRIAL DISPUTES SUITE ---
def generate_labour_claim(workman, employer, termination_date, back_wages):
    os.makedirs("labour_claims", exist_ok=True)
    safe_work = _safe_name(workman)
    path = f"labour_claims/labour_claim_{safe_work}.md"
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
