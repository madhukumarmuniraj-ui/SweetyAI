import os
import sys
import re
import calendar
import datetime
import argparse

NI138_OUT_DIR = "ni138_complaints"


def add_calendar_months(source_date, months):
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def parse_ymd(date_str, label):
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print(f"[Error] Invalid {label} '{date_str}'. Expected format: YYYY-MM-DD.")
        sys.exit(1)


def compute_ni138_timeline(
    cheque_date_str,
    presentation_date_str,
    dishonour_date_str,
    notice_date_str,
    service_date_str=None,
):
    cheque_dt = parse_ymd(cheque_date_str, "cheque-date")
    pres_dt = parse_ymd(presentation_date_str, "presentation-date")
    memo_dt = parse_ymd(dishonour_date_str, "dishonour-date")
    notice_dt = parse_ymd(notice_date_str, "notice-date")

    # If service_date is omitted, apply deemed service on 4th day from RPAD dispatch (Sec. 27 General Clauses Act)
    deemed_service_used = False
    if service_date_str:
        service_dt = parse_ymd(service_date_str, "service-date")
    else:
        service_dt = notice_dt + datetime.timedelta(days=4)
        deemed_service_used = True

    today = datetime.date.today()

    # Gate 1: 3-Month Cheque Validity (Rameshchandra Ambalal Joshi v. State of Gujarat, (2014) 11 SCC 759)
    cheque_expiry_dt = add_calendar_months(cheque_dt, 3)
    gate1_valid = cheque_dt <= pres_dt <= cheque_expiry_dt
    gate1_status = (
        f"COMPLIANT (Presented within {(pres_dt - cheque_dt).days} days; valid until {cheque_expiry_dt.strftime('%d.%m.%Y')})"
        if gate1_valid
        else f"DEFECTIVE / STALE CHEQUE (Presented on {pres_dt.strftime('%d.%m.%Y')}; 3-month validity expired on {cheque_expiry_dt.strftime('%d.%m.%Y')})"
    )

    # Gate 2: 30-Day Statutory Demand Notice Window (Sec. 138 Proviso (b) - Date of Memo Excluded)
    notice_deadline_dt = memo_dt + datetime.timedelta(days=30)
    days_to_notice = (notice_dt - memo_dt).days
    gate2_valid = 0 <= days_to_notice <= 30
    gate2_status = (
        f"COMPLIANT (Dispatched on Day {days_to_notice} of 30; outer deadline was {notice_deadline_dt.strftime('%d.%m.%Y')})"
        if gate2_valid
        else f"TIME-BARRED NOTICE (Dispatched after {days_to_notice} days on {notice_dt.strftime('%d.%m.%Y')}; 30-day statutory deadline expired on {notice_deadline_dt.strftime('%d.%m.%Y')} — Non-condonable)"
    )

    # Gate 3: 15 Clear Days Grace Period for Payment (Sec. 138 Proviso (c) - Yogendra Pratap Singh v. Savitri Pandey)
    # Service date is excluded; 15 clear days = service_dt + 1 day through service_dt + 15 days
    grace_start_dt = service_dt + datetime.timedelta(days=1)
    grace_end_dt = service_dt + datetime.timedelta(days=15)

    # Gate 4: Cause of Action & 1-Month Limitation Window (Sec. 142(1)(b) - Econ Antri Ltd. v. Rom Industries Ltd.)
    # Cause of action arises on Day 16 after service (grace_end_dt + 1 day).
    # Per Econ Antri (3-Judge Bench), the day cause of action arises is excluded for the 1-month window:
    # Therefore, 1 calendar month runs from (cause_of_action_dt + 1 day) to add_calendar_months(cause_of_action_dt, 1).
    cause_of_action_dt = grace_end_dt + datetime.timedelta(days=1)
    limitation_last_dt = add_calendar_months(cause_of_action_dt, 1)

    if today <= grace_end_dt:
        wait_days = (cause_of_action_dt - today).days
        filing_status = (
            f"PREMATURE TO FILE TODAY (Wait {wait_days} more day(s)! "
            f"15-day grace period expires on {grace_end_dt.strftime('%d.%m.%Y')}. "
            f"Earliest valid filing date is {cause_of_action_dt.strftime('%d.%m.%Y')} per Yogendra Pratap Singh v. Savitri Pandey, (2014) 10 SCC 713)"
        )
        condonation_needed = False
    elif cause_of_action_dt <= today <= limitation_last_dt:
        rem_days = (limitation_last_dt - today).days
        filing_status = (
            f"RIPE & WITHIN LIMITATION ({rem_days} day(s) remaining; "
            f"valid filing window: {cause_of_action_dt.strftime('%d.%m.%Y')} to {limitation_last_dt.strftime('%d.%m.%Y')})"
        )
        condonation_needed = False
    else:
        delay_days = (today - limitation_last_dt).days
        filing_status = (
            f"DELAY OF {delay_days} DAY(S) BEYOND 1-MONTH WINDOW (Expired on {limitation_last_dt.strftime('%d.%m.%Y')}). "
            f"Requires Application for Condonation of Delay under the Proviso to Section 142(1)(b) of the NI Act, 1881."
        )
        condonation_needed = True

    return {
        "cheque_dt": cheque_dt,
        "pres_dt": pres_dt,
        "memo_dt": memo_dt,
        "notice_dt": notice_dt,
        "service_dt": service_dt,
        "deemed_service_used": deemed_service_used,
        "cheque_expiry_dt": cheque_expiry_dt,
        "gate1_valid": gate1_valid,
        "gate1_status": gate1_status,
        "notice_deadline_dt": notice_deadline_dt,
        "gate2_valid": gate2_valid,
        "gate2_status": gate2_status,
        "grace_start_dt": grace_start_dt,
        "grace_end_dt": grace_end_dt,
        "cause_of_action_dt": cause_of_action_dt,
        "limitation_last_dt": limitation_last_dt,
        "filing_status": filing_status,
        "condonation_needed": condonation_needed,
    }


def generate_ni138_bundle(
    complainant,
    accused,
    cheque_no,
    amount,
    cheque_date_str,
    presentation_date_str,
    dishonour_date_str,
    notice_date_str,
    service_date_str=None,
    drawee_bank="HDFC Bank Ltd., Bengaluru Branch",
    payee_bank="State Bank of India, Bengaluru Branch",
    return_reason="Funds Insufficient",
    liability_desc="towards discharge of a legally enforceable debt and commercial liability",
):
    os.makedirs(NI138_OUT_DIR, exist_ok=True)
    tl = compute_ni138_timeline(
        cheque_date_str,
        presentation_date_str,
        dishonour_date_str,
        notice_date_str,
        service_date_str,
    )
    today_str = datetime.date.today().strftime("%d.%m.%Y")
    interim_20_pct = amount * 0.20
    double_fine = amount * 2.0

    service_note = (
        f"{tl['service_dt'].strftime('%d.%m.%Y')} (Deemed service under Sec. 27 General Clauses Act)"
        if tl["deemed_service_used"]
        else f"{tl['service_dt'].strftime('%d.%m.%Y')} (Actual Postal Tracking / AD Card Delivery)"
    )

    bundle_md = f"""# IN THE COURT OF THE ADDITIONAL CHIEF JUDICIAL MAGISTRATE (ACJM / SPECIAL COURT FOR NI ACT CASES) AT BENGALURU

## P.C.R. No. ____________ / 2026
*(Private Complaint under Section 223 of the Bharatiya Nagarik Suraksha Sanhita, 2023 read with Sections 138, 141 & 142 of the Negotiable Instruments Act, 1881)*

**BETWEEN:**

**{complainant}**
... **COMPLAINANT**

**AND:**

**{accused}**
... **ACCUSED**

---

## I. STATUTORY TIMELINE & LIMITATION COMPLIANCE MATRIX (SECTIONS 138 & 142 NI ACT)

| Statutory Gate | Relevant Date | Statutory Limit / Deadline | Audit Verdict |
| :--- | :--- | :--- | :--- |
| **1. Date Drawn on Cheque (`Ex. P-1`)** | **{tl['cheque_dt'].strftime('%d.%m.%Y')}** | Valid for 3 Months (up to **{tl['cheque_expiry_dt'].strftime('%d.%m.%Y')}**) | Cheque No. `{cheque_no}` for **INR {amount:,.2f}** |
| **2. Presentation at Payee Bank** | **{tl['pres_dt'].strftime('%d.%m.%Y')}** | Must reach Drawee Bank by **{tl['cheque_expiry_dt'].strftime('%d.%m.%Y')}** | `{tl['gate1_status']}` |
| **3. Bank Dishonour Memo (`Ex. P-2`)** | **{tl['memo_dt'].strftime('%d.%m.%Y')}** | Endorsement: *"{return_reason}"* | Triggers 30-day notice window |
| **4. Legal Demand Notice (`Ex. P-3`)** | **{tl['notice_dt'].strftime('%d.%m.%Y')}** | 30 Days from Memo (Deadline: **{tl['notice_deadline_dt'].strftime('%d.%m.%Y')}**) | `{tl['gate2_status']}` |
| **5. Service of Legal Notice (`Ex. P-5`)** | **{service_note}** | Starts 15 clear days payment window | Governed by *C.C. Alavi Haji v. Palapetty Muhammed*, (2007) 6 SCC 555 |
| **6. 15-Day Payment Grace Period** | **{tl['grace_start_dt'].strftime('%d.%m.%Y')} to {tl['grace_end_dt'].strftime('%d.%m.%Y')}** | 15 Clear Days under Sec. 138 Proviso (c) | No payment made by Accused within 15 days |
| **7. Date Cause of Action Arose (Day 16)** | **{tl['cause_of_action_dt'].strftime('%d.%m.%Y')}** | Earliest valid filing date (*Yogendra Pratap Singh*) | Excluded in 1-month count per *Econ Antri Ltd.*, (2014) 11 SCC 769 |
| **8. Last Date to File (Sec. 142(1)(b))** | **{tl['limitation_last_dt'].strftime('%d.%m.%Y')}** | 1 Calendar Month from Cause of Action | **`{tl['filing_status']}`** |

---

## II. MEMORANDUM OF PRIVATE COMPLAINT UNDER SECTION 223 OF THE BHARATIYA NAGARIK SURAKSHA SANHITA, 2023 READ WITH SECTIONS 138 & 142 OF THE NEGOTIABLE INSTRUMENTS ACT, 1881

The Complainant above named most respectfully submits as follows:

1. **DESCRIPTION OF PARTIES:**
   The Complainant and the Accused are described in the Cause Title above. The Complainant is a law-abiding citizen / entity maintaining its regular bank account at **{payee_bank}**, within the territorial jurisdiction of this Hon'ble Court.

2. **LEGALLY ENFORCEABLE DEBT / LIABILITY (SECTION 138 EXPLANATION & SECTION 139 PRESUMPTION):**
   The Accused approached the Complainant and incurred a legally enforceable debt and liability of **INR {amount:,.2f}** ({liability_desc}). Under **Sections 118(a) and 139 of the Negotiable Instruments Act, 1881**, a mandatory statutory presumption arises that the cheque was drawn for the discharge of a legally enforceable debt or liability (*Rangappa v. Sri Mohan*, (2010) 11 SCC 441).

3. **ISSUANCE OF THE SUBJECT CHEQUE:**
   Towards the discharge of the aforesaid legally enforceable debt, the Accused issued Cheque bearing **No. {cheque_no}** dated **{tl['cheque_dt'].strftime('%d.%m.%Y')}** for a sum of **INR {amount:,.2f}** drawn on **{drawee_bank}** in favour of the Complainant, assuring the Complainant that the said cheque would be honoured upon presentation.

4. **PRESENTATION & DISHONOUR OF CHEQUE:**
   Acting upon the assurances of the Accused, the Complainant presented the said Cheque bearing No. `{cheque_no}` on **{tl['pres_dt'].strftime('%d.%m.%Y')}** (well within its 3-month statutory validity period) for collection through the Complainant's bank account maintained at **{payee_bank}**. However, the said cheque was returned dishonoured with the Bank Return Memo dated **{tl['memo_dt'].strftime('%d.%m.%Y')}** carrying the endorsement **"{return_reason}"**.

5. **STATUTORY DEMAND NOTICE UNDER SECTION 138 PROVISO (b):**
   Within the statutory period of thirty (30) days from the receipt of the dishonour memo, the Complainant caused a Statutory Legal Demand Notice dated **{tl['notice_dt'].strftime('%d.%m.%Y')}** to be issued to the Accused by Registered Post Acknowledgement Due (RPAD) / Speed Post, calling upon the Accused to pay the cheque amount of **INR {amount:,.2f}** within fifteen (15) days from the date of receipt of the notice.

6. **SERVICE OF NOTICE & DEFAULT UNDER SECTION 138 PROVISO (c):**
   The said Statutory Legal Notice was duly served on the Accused on **{tl['service_dt'].strftime('%d.%m.%Y')}**. Despite due service of notice and expiry of the statutory grace period of fifteen (15) clear days on **{tl['grace_end_dt'].strftime('%d.%m.%Y')}**, the Accused failed and neglected to pay the cheque amount of **INR {amount:,.2f}**. Consequently, the cause of action to file the present complaint accrued on **{tl['cause_of_action_dt'].strftime('%d.%m.%Y')}**.

7. **TERRITORIAL JURISDICTION UNDER SECTION 142(2)(a) OF THE NI ACT:**
   The cheque in question was delivered for collection through the Complainant's bank account maintained at **{payee_bank}**, which is situated within the local territorial limits of this Hon'ble Court at Bengaluru under **Section 142(2)(a) of the Negotiable Instruments Act, 1881**.

8. **PROCEDURE UNDER SECTION 223 BNSS, 2023 READ WITH SECTIONS 4(2) & 5 BNSS AND SECTIONS 142–145 NI ACT:**
   The Complainant has filed his Sworn Statement by way of Affidavit under **Section 145(1) of the Negotiable Instruments Act, 1881** along with original documents (`Exhibits P-1 to P-6`) in accordance with the Constitution Bench directions in *In Re: Expeditious Trial of Cases Under Section 138 of NI Act*, (2021) 16 SCC 116 and *Indian Bank Association v. Union of India*, (2014) 5 SCC 590. Without prejudice to the *sui generis* summary procedure saved by **Section 5 of the BNSS, 2023**, the Complainant prays that this Hon'ble Court may issue pre-cognizance notice to the Accused under the **First Proviso to Section 223(1) of the BNSS, 2023** (if deemed applicable) and/or take cognizance of the offence punishable under Section 138 of the NI Act and issue process under **Section 227 of the BNSS, 2023**.
"""

    if tl["condonation_needed"]:
        bundle_md += f"""
9. **APPLICATION FOR CONDONATION OF DELAY UNDER PROVISO TO SECTION 142(1)(b) NI ACT:**
   There is a brief delay beyond the 1-month window expiring on {tl['limitation_last_dt'].strftime('%d.%m.%Y')}. The Complainant has filed a separate Application under the **Proviso to Section 142(1)(b) of the Negotiable Instruments Act, 1881** demonstrating sufficient cause for condonation of the said delay.
"""

    bundle_md += f"""
---

## III. PRAYER IN PRIVATE COMPLAINT

**WHEREFORE**, the Complainant most respectfully prays that this Hon'ble Court may be pleased to:

1. **TAKE COGNIZANCE** of the offence committed by the Accused punishable under **Section 138 of the Negotiable Instruments Act, 1881** (after complying with Section 223(1) Proviso BNSS, if required), register the case, and issue summons/process to the Accused under **Section 227 of the Bharatiya Nagarik Suraksha Sanhita, 2023**;
2. **CONVICT AND SENTENCE** the Accused for the offence punishable under **Section 138 of the Negotiable Instruments Act, 1881** with imprisonment for a term which may extend to two (2) years, and impose a fine extending to twice the amount of the cheque (**INR {double_fine:,.2f}**);
3. **AWARD COMPENSATION** to the Complainant under **Section 395 of the Bharatiya Nagarik Suraksha Sanhita, 2023** (formerly Section 357 CrPC) read with Section 138 of the NI Act out of the fine amount recovered, together with interest at 18% per annum under Section 80 of the NI Act; and
4. Pass such other and further orders as this Hon'ble Court deems fit in the interest of justice.

**BENGALURU**  
**DATE: {today_str}**  

**COMPLAINANT**                                           **ADVOCATE FOR THE COMPLAINANT**

---

## IV. SWORN STATEMENT BY WAY OF AFFIDAVIT UNDER SECTION 145(1) OF THE NI ACT, 1881 READ WITH SECTION 223 OF THE BNSS, 2023
*(Per Indian Bank Association v. Union of India, (2014) 5 SCC 590)*

I, **{complainant}**, do hereby solemnly affirm and state on oath as follows:

1. I am the Complainant in the above case and I am well conversant with the facts and circumstances of the transaction. I am swearing to this Affidavit by way of my Sworn Statement / Examination-in-Chief under **Section 145(1) of the Negotiable Instruments Act, 1881** read with **Section 223 of the Bharatiya Nagarik Suraksha Sanhita, 2023**.
2. I repeat, reiterate, and adopt the averments made in Paragraphs 1 to 8 of the accompanying Private Complaint as part and parcel of this Sworn Statement.
3. I tender the following original documents for marking as Exhibits in support of my complaint:
   - **Exhibit P-1:** Original Dishonoured Cheque No. `{cheque_no}` dated `{tl['cheque_dt'].strftime('%d.%m.%Y')}` for **INR {amount:,.2f}** drawn on `{drawee_bank}`.
   - **Exhibit P-1(a):** Signature of the Accused on Exhibit P-1.
   - **Exhibit P-2:** Original Bank Return Memo / Endorsement dated `{tl['memo_dt'].strftime('%d.%m.%Y')}` showing dishonour for *"{return_reason}"*.
   - **Exhibit P-3:** Office Copy of the Statutory Legal Demand Notice dated `{tl['notice_dt'].strftime('%d.%m.%Y')}`.
   - **Exhibit P-4:** Original Postal Receipt(s) dated `{tl['notice_dt'].strftime('%d.%m.%Y')}`.
   - **Exhibit P-5:** Original Postal Acknowledgement Due Card / Consignment Delivery Track Report confirming delivery on `{tl['service_dt'].strftime('%d.%m.%Y')}`.
   - **Exhibit P-6:** Underlying Invoice / Agreement / Ledger Account Statement evidencing the legally enforceable debt.
4. The complaint is filed within the statutory period prescribed under Section 142(1)(b) of the NI Act, 1881, and all statutory requirements under Section 138 Provisos (a), (b), and (c) have been strictly complied with.

**Identified by me:**

**ADVOCATE**                                                      **DEPONENT (COMPLAINANT)**  
**BENGALURU**  
**DATE: {today_str}**

---

## V. APPLICATION UNDER SECTION 143A OF THE NEGOTIABLE INSTRUMENTS ACT, 1881 FOR GRANT OF 20% INTERIM COMPENSATION

The Complainant above named most respectfully submits as follows:

1. The Complainant has filed the accompanying Private Complaint under Section 138 of the NI Act in respect of Dishonoured Cheque No. `{cheque_no}` for **INR {amount:,.2f}**.
2. Under **Section 143A(1) & (2) of the Negotiable Instruments Act, 1881**, this Hon'ble Court is empowered to direct the drawer of the cheque to pay interim compensation up to **twenty percent (20%)** of the amount of the cheque upon the Accused pleading not guilty to the accusation made in the complaint.
3. Applying the parameters laid down by the Hon'ble Supreme Court in *Rakesh Ranjan Shrivastava v. State of Jharkhand*, (2024) 4 SCC 419 (2024 INSC 205):
   - **(i) Prima Facie Merits:** The issuance of the cheque, signature of the Accused, bank return memo, and service of statutory notice establish an overwhelming prima facie case supported by documentary evidence (`Ex. P-1 to P-6`).
   - **(ii) Conduct of the Accused & Financial Prejudice:** The Accused has unjustly withheld **INR {amount:,.2f}** since **{tl['cheque_dt'].strftime('%d.%m.%Y')}** and failed to comply with the statutory demand notice, causing severe financial hardship to the Complainant.
4. **PRAYER IN I.A. UNDER SECTION 143A NI ACT:**
   Wherefore, the Complainant prays that this Hon'ble Court may be pleased to direct the Accused to pay **20% of the cheque amount**, i.e., **INR {interim_20_pct:,.2f}**, as Interim Compensation to the Complainant within sixty (60) days under **Section 143A(2) & (3) of the Negotiable Instruments Act, 1881**, recoverable as a fine under **Section 461 of the BNSS, 2023** (formerly Section 421 CrPC) in case of default.

**BENGALURU**  
**DATE: {today_str}**  

**ADVOCATE FOR THE COMPLAINANT**

---

## VI. LIST OF WITNESSES & LIST OF DOCUMENTS
1. **Witnesses:**
   - **CW-1:** {complainant} (Complainant)
   - **CW-2:** Branch Manager / Authorized Officer, {payee_bank}
   - **CW-3:** Branch Manager / Authorized Officer, {drawee_bank}
2. **Documents Produced:** Exhibits P-1 to P-6 as enumerated in Paragraph 3 of the Sworn Statement Affidavit above.
"""

    slug = re.sub(r"[^A-Za-z0-9]", "_", cheque_no).strip("_").lower()
    out_path = os.path.join(NI138_OUT_DIR, f"ni138_pcr_bundle_cheque_{slug}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(bundle_md)

    print("\n=== SweetyAI Section 138 NI Act Calculator & P.C.R. Bundle Generator ===")
    print(f"Cheque Details      : No. {cheque_no} | INR {amount:,.2f} | Drawn: {tl['cheque_dt'].strftime('%d.%m.%Y')}")
    print(f"Gate 1 (3m Pres.)   : {tl['gate1_status']}")
    print(f"Gate 2 (30d Notice) : {tl['gate2_status']}")
    print(f"Gate 3 (15d Grace)  : {tl['grace_start_dt'].strftime('%d.%m.%Y')} to {tl['grace_end_dt'].strftime('%d.%m.%Y')}")
    print(f"Gate 4 (Sec 142)    : {tl['filing_status']}")
    print(f"Sec 143A (20% Cap)  : INR {interim_20_pct:,.2f}")
    print("=========================================================================")
    print(f"[Success] Complete Section 138 NI Act Filing Bundle saved -> '{out_path}'")
    print(f"          (Run `python3 sweety.py export {out_path}` for A4 Court-Ready HTML)")
    print("=========================================================================\n")


def handle_ni138_cli(argv):
    parser = argparse.ArgumentParser(
        prog="sweety legal ni138",
        description="Section 138 NI Act Statutory Timeline Calculator & Section 223 BNSS Private Complaint (P.C.R.) Generator.",
    )
    parser.add_argument("--cheque-date", required=True, help="Date drawn on the cheque (YYYY-MM-DD)")
    parser.add_argument("--presentation-date", required=True, help="Date cheque presented at bank (YYYY-MM-DD)")
    parser.add_argument("--dishonour-date", required=True, help="Date of Bank Return Memo / intimation (YYYY-MM-DD)")
    parser.add_argument("--notice-date", required=True, help="Date Legal Demand Notice dispatched (YYYY-MM-DD)")
    parser.add_argument("--service-date", default=None, help="Date Legal Notice served on Accused (YYYY-MM-DD; defaults to +4 days deemed service)")
    parser.add_argument("--amount", type=float, required=True, help="Cheque amount in INR")
    parser.add_argument("--cheque-no", default="458921", help="6-digit Cheque Number")
    parser.add_argument("--complainant", default="Sri [Name of Complainant], R/at Bengaluru", help="Complainant name and address")
    parser.add_argument("--accused", default="Sri [Name of Accused], R/at Bengaluru", help="Accused name and address")
    parser.add_argument("--drawee-bank", default="HDFC Bank Ltd., M.G. Road Branch, Bengaluru", help="Accused's bank branch (Drawee Bank)")
    parser.add_argument("--payee-bank", default="State Bank of India, St. Marks Road Branch, Bengaluru", help="Complainant's bank branch (for Sec. 142(2)(a) jurisdiction)")
    parser.add_argument("--return-reason", default="Funds Insufficient", help="Dishonour endorsement on Bank Return Memo")
    parser.add_argument("--liability", default="towards discharge of a legally enforceable commercial debt", help="Brief description of debt/liability")
    args = parser.parse_args(argv)

    generate_ni138_bundle(
        complainant=args.complainant,
        accused=args.accused,
        cheque_no=args.cheque_no,
        amount=args.amount,
        cheque_date_str=args.cheque_date,
        presentation_date_str=args.presentation_date,
        dishonour_date_str=args.dishonour_date,
        notice_date_str=args.notice_date,
        service_date_str=args.service_date,
        drawee_bank=args.drawee_bank,
        payee_bank=args.payee_bank,
        return_reason=args.return_reason,
        liability_desc=args.liability,
    )


if __name__ == "__main__":
    handle_ni138_cli(sys.argv[1:])
