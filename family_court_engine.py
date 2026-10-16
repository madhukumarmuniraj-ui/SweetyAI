"""
SweetyAI Module 27: Family Court & Matrimonial Litigation Suite
Hindu Marriage Act, 1955 divorce/maintenance petition generators and
BNSS maintenance application suite for the Family Court.
"""

import os
import argparse
from datetime import datetime


def _safe_name(name):
    return "".join(c if c.isalnum() else "_" for c in name)


# --- MODULE 27A: SEC. 13 HMA DIVORCE PETITION ---
def generate_divorce_petition(
    petitioner,
    respondent,
    marriage_date,
    grounds="cruelty and desertion under Section 13(1)(ia) and (ib) of the Hindu Marriage Act, 1955",
    relief="dissolution of marriage by a decree of divorce and permanent alimony",
):
    os.makedirs("family_court_petitions", exist_ok=True)
    safe_pet = _safe_name(petitioner)
    path = f"family_court_petitions/divorce_petition_{safe_pet}.md"
    content = f"""# IN THE COURT OF THE PRINCIPAL JUDGE, FAMILY COURT AT BENGALURU
M.C. NO. _________ OF 2026

**BETWEEN:**
**{petitioner}**                                                 ... PETITIONER
**AND:**
**{respondent}**                                                 ... RESPONDENT

---

## PETITION UNDER SECTION 13(1) OF THE HINDU MARRIAGE ACT, 1955

1. **Marriage:** The marriage between the Petitioner and the Respondent was solemnized on `{marriage_date}` at Bengaluru according to Hindu rites and customs, and is registered/registrable under the Karnataka Marriages (Registration and Miscellaneous Provisions) Act, 1976.
2. **Grounds for Divorce:** The marriage has broken down irretrievably on account of {grounds}. The Respondent's conduct has caused the Petitioner severe mental cruelty, and the parties have lived separately without cohabitation, with no reasonable prospect of reunion.
3. **No Collusion / No Prior Proceedings:** This petition is not presented in collusion with the Respondent. No other petition for divorce, judicial separation or restitution of conjugal rights is pending between the parties before any court.
4. **Mediation:** The Petitioner is willing to participate in court-annexed mediation as mandated under Section 9 of the Family Courts Act, 1984, though the circumstances render reconciliation improbable.
5. **Alimony & Interim Relief:** The Petitioner seeks {relief}, along with interim maintenance under Section 24 of the Hindu Marriage Act, 1955 and litigation expenses.

## PRAYER
It is therefore prayed that this Hon'ble Court be pleased to: (a) dissolve the marriage solemnized on `{marriage_date}` by a decree of divorce under Section 13(1) of the Hindu Marriage Act, 1955; (b) grant {relief}; and (c) pass such further orders as are just and proper.

**Advocate for the Petitioner**
Place: Bengaluru
Date: {datetime.now().strftime('%d.%m.%Y')}
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Success] Divorce Petition saved -> '{path}'")


# --- MODULE 27B: SEC. 144 BNSS (SEC. 125 CRPC) MAINTENANCE APPLICATION ---
def generate_maintenance_application(
    applicant,
    respondent,
    monthly_income,
    claimed_maintenance,
    child_name=None,
):
    os.makedirs("family_court_petitions", exist_ok=True)
    safe_app = _safe_name(applicant)
    path = f"family_court_petitions/maintenance_application_{safe_app}.md"
    dependants = f"the Applicant and the minor child {child_name}" if child_name else "the Applicant"
    content = f"""# IN THE COURT OF THE JUDICIAL MAGISTRATE FIRST CLASS / FAMILY COURT AT BENGALURU
CRIMINAL MISC. NO. _________ OF 2026
(Application under Section 144 of the Bharatiya Nagarik Suraksha Sanhita, 2023 — corresponding to Section 125 Cr.P.C.)

**BETWEEN:**
**{applicant}**                                                  ... APPLICANT
**AND:**
**{respondent}**                                                 ... RESPONDENT

---

1. **Relationship:** The Applicant is the legally wedded wife/widow/child of the Respondent and is unable to maintain herself/himself, whereas the Respondent has sufficient means — a monthly income of not less than **INR {monthly_income:,.2f}** from known sources.
2. **Neglect:** The Respondent has neglected and refused to maintain {dependants}, compelling this application for monthly maintenance under Section 144 BNSS, 2023.
3. **Quantum:** Having regard to the standard of living of the parties and the Respondent's means, a sum of **INR {claimed_maintenance:,.2f} per month** is claimed for {dependants}, payable from the date of this application, with a modest sum towards litigation costs.
4. **No Bar:** The Applicant is not in receipt of any maintenance from any other source, and no other proceeding for maintenance on the same Cause of Action is pending between the parties.

## PRAYER
It is therefore prayed that this Hon'ble Court be pleased to direct the Respondent to pay monthly maintenance of **INR {claimed_maintenance:,.2f}** to the Applicant under Section 144 of the BNSS, 2023, with litigation costs, and pass such further orders as are just and proper.

**Advocate for the Applicant**
Place: Bengaluru
Date: {datetime.now().strftime('%d.%m.%Y')}
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Success] Maintenance Application saved -> '{path}'")


def handle_family_cli(args):
    p = argparse.ArgumentParser(prog="sweety legal family-court")
    p.add_argument("--mode", "--type", dest="mode", default="divorce",
                   help="divorce (Sec. 13 HMA) | maintenance | sec144 (Sec. 144 BNSS maintenance)")
    p.add_argument("--petitioner", default="Smt. Ananya Rao")
    p.add_argument("--respondent", default="Sri. Vikram Rao")
    p.add_argument("--marriage-date", default="2018-11-25")
    p.add_argument("--grounds", default="cruelty and desertion under Section 13(1)(ia) and (ib) of the Hindu Marriage Act, 1955")
    p.add_argument("--relief", default="dissolution of marriage by a decree of divorce and permanent alimony of INR 25,000 per month")
    p.add_argument("--income", type=float, default=180000.0, help="Respondent's monthly income")
    p.add_argument("--amount", type=float, default=30000.0, help="Claimed monthly maintenance")
    p.add_argument("--child", default=None, help="Name of minor child, if any")
    a = p.parse_args(args)

    if a.mode in ("maintenance", "sec144", "125", "sec125"):
        generate_maintenance_application(a.petitioner, a.respondent, a.income, a.amount, a.child)
    else:
        generate_divorce_petition(a.petitioner, a.respondent, a.marriage_date, a.grounds, a.relief)


if __name__ == "__main__":
    import sys
    handle_family_cli(sys.argv[1:])
