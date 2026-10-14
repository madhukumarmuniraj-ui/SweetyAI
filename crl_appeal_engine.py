import os
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
        "IN THE HIGH COURT OF KARNATAKA AT BENGALURU\n(APPELLATE JURISDICTION)\nCRIMINAL APPEAL NO. _________ OF 2026"
        if forum == "hc"
        else "IN THE COURT OF THE PRINCIPAL CITY CIVIL AND SESSIONS JUDGE AT BENGALURU (CCH-1)\nCRIMINAL APPEAL NO. _________ OF 2026"
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
    print(f"\n[Success] Criminal Appeal & Sec. 430 BNSS Suspension Bundle saved -> '{out_path}'")
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
