import os
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
    print(f"\n[Success] Commercial Suit, Sec. 12A PIM & Statement of Truth saved -> '{out_path}'")
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
