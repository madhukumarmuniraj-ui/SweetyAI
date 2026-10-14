import os
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
    print(f"\n[Success] IBC Section 8 Form 3 & Section 9 Form 5 NCLT Bundle saved -> '{out_path}'")
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
