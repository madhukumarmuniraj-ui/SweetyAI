"""
SweetyAI Module 26: MSME Delayed Payment & MSEFC Reference Engine
MSMED Act, 2006 (as amended) Section 18 MSEFC reference generator with
Section 16 compound interest computation (3x RBI bank rate, compounded monthly).
"""

import os
import argparse
from datetime import datetime


def _safe_name(name):
    return "".join(c if c.isalnum() else "_" for c in name)


def compute_msme_interest(amount, delayed_days, bank_rate=6.5):
    """Section 16 MSMED Act: compound interest at 3x the RBI bank rate, compounded monthly."""
    annual_rate = (bank_rate * 3.0) / 100.0
    monthly_rate = annual_rate / 12.0
    months = delayed_days / 30.0
    if amount <= 0 or months <= 0:
        return 0.0
    return amount * ((1.0 + monthly_rate) ** months) - amount


# --- MODULE 26: MSMED ACT SEC. 18 MSEFC REFERENCE & 3X RBI COMPOUND INTEREST ---
def generate_msme_reference(
    supplier,
    buyer,
    invoice_no,
    invoice_date,
    amount,
    delayed_days,
    bank_rate=6.5,
    acceptance_date=None,
):
    os.makedirs("msme_references", exist_ok=True)
    safe_sup = _safe_name(supplier)
    path = f"msme_references/msme_msefc_reference_{safe_sup}.md"

    interest = compute_msme_interest(amount, delayed_days, bank_rate)
    total = amount + interest

    content = f"""# BEFORE THE MICRO AND SMALL ENTERPRISES FACILITATION COUNCIL (MSEFC), BENGALURU
MSEFC REFERENCE NO. _________ OF 2026

**BETWEEN:**
**{supplier}** (Udyam Registered Micro/Small Enterprise)      ... APPLICANT / SUPPLIER
**AND:**
**{buyer}**                                                    ... RESPONDENT / BUYER

---

## REFERENCE UNDER SECTION 18 OF THE MICRO, SMALL AND MEDIUM ENTERPRISES DEVELOPMENT ACT, 2006

1. **Supply & Invoice:** The Applicant supplied goods/services to the Respondent vide Invoice No. `{invoice_no}` dated `{invoice_date}` for **INR {amount:,.2f}**, which were accepted / deemed accepted on `{acceptance_date or invoice_date}`.
2. **Statutory Payment Period (Sec. 15):** The Respondent was bound to pay the agreed consideration within **45 days** from the day of acceptance/deemed acceptance of the goods/services.
3. **Default:** Payment has remained outstanding for approximately **{delayed_days} days** beyond the statutory period, necessitating this reference.
4. **Compound Interest (Sec. 16):** Under Section 16(1) of the MSMED Act, interest is payable at **three times the RBI bank rate** (taken as {bank_rate}% p.a.) **compounded monthly** from the appointed day:
   - Principal: **INR {amount:,.2f}**
   - Compound interest @{bank_rate * 3:.2f}% p.a. (compounded monthly) for {delayed_days} days: **INR {interest:,.2f}**
   - **Total claim: INR {total:,.2f}** (further interest continues to accrue till realisation).
5. **Jurisdiction & No Prior Reference:** The dispute is within the pecuniary jurisdiction of this Council, and no reference on the same cause of action has been made to any other Council, court, or authority.
6. **Section 19 Deposit:** It is submitted that the Respondent cannot maintain any application under Section 19 while remaining in default of the deposit requirement of **75%** of the amount due.

## PRAYER
It is therefore prayed that this Hon'ble Council be pleased to issue a direction under Section 18(3) of the MSMED Act, 2006 directing the Respondent to pay the Applicant **INR {total:,.2f}** together with compound interest under Section 16 till realisation, and pass such further orders as are just and proper.

**Applicant / Advocate for the Applicant**
Place: Bengaluru
Date: {datetime.now().strftime('%d.%m.%Y')}
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Success] MSME MSEFC Reference saved -> '{path}' (interest: INR {interest:,.2f})")


def handle_msme_cli(args):
    p = argparse.ArgumentParser(prog="sweety legal msme")
    p.add_argument("--supplier", default="M/s. Precision Toolings (Udyam: UDYAM-KR-03-0012345)")
    p.add_argument("--buyer", default="M/s. Orion Infra LLP")
    p.add_argument("--invoice-no", default="INV/2026/0842")
    p.add_argument("--invoice-date", default="2026-02-01")
    p.add_argument("--principal", "--amount", dest="amount", type=float, default=1850000.0,
                   help="Outstanding principal amount (alias: --amount)")
    p.add_argument("--acceptance-date", default=None,
                   help="Date the goods/services were accepted (YYYY-MM-DD); delayed days are computed from the 45-day statutory window")
    p.add_argument("--delayed-days", type=int, default=180)
    p.add_argument("--bank-rate", type=float, default=6.5, help="RBI bank rate, %% p.a. (interest = 3x this rate, compounded monthly)")
    a = p.parse_args(args)

    delayed_days = a.delayed_days
    if a.acceptance_date:
        try:
            accepted_on = datetime.strptime(a.acceptance_date, "%Y-%m-%d").date()
            delayed_days = max((datetime.now().date() - accepted_on).days - 45, 0)
        except ValueError:
            print(f"[Warning] Could not parse --acceptance-date '{a.acceptance_date}'; using --delayed-days={a.delayed_days}.")

    generate_msme_reference(a.supplier, a.buyer, a.invoice_no, a.invoice_date, a.amount, delayed_days,
                            a.bank_rate, acceptance_date=a.acceptance_date)


if __name__ == "__main__":
    import sys
    handle_msme_cli(sys.argv[1:])
