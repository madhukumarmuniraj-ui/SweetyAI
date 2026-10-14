import os
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
    print(f"\n[Success] Arbitration Sec. 21, Sec. 9 & Sec. 11(6) C.M.P. Suite saved -> '{out_path}'")
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
