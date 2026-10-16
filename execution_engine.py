"""
SweetyAI Module 25: Execution & Award Enforcement Engine
Order XXI Rule 11(2) CPC Execution Petition generator and Section 36
Arbitration & Conciliation Act, 1996 award-enforcement suite.
"""

import os
import argparse
from datetime import datetime


def _safe_name(name):
    return "".join(c if c.isalnum() else "_" for c in name)


# --- MODULE 25: ORDER XXI RULE 11(2) CPC EXECUTION & SEC. 36 AWARD ENFORCEMENT ---
def generate_execution_petition(
    decree_holder,
    judgment_debtor,
    decree_date,
    decretal_amount,
    mode="attachment and sale of movable/immovable property, and garnishee of bank accounts",
    decree_nature="Decree/Award",
    case_no=None,
    commercial=False,
):
    os.makedirs("execution_petitions", exist_ok=True)
    safe_dh = _safe_name(decree_holder)
    path = f"execution_petitions/execution_petition_{safe_dh}.md"
    interest_amount = decretal_amount * 0.09  # indicative post-decree interest @9% p.a.
    case_note = (
        f" This execution petition arises out of the proceedings in `{case_no}`."
        if case_no else ""
    )
    commercial_note = (
        "\n6. **Commercial Dispute:** The underlying dispute is commercial in nature "
        "(Commercial Courts Act, 2015), and the full machinery of Order XXI CPC is "
        "prayed to be exercised in this execution."
        if commercial else ""
    )
    content = f"""# IN THE COURT OF THE DISTRICT JUDGE / PRINCIPAL CITY CIVIL JUDGE AT BENGALURU
EXECUTION CASE NO. _________ OF 2026

**BETWEEN:**
**{decree_holder}**                                             ... DECREE HOLDER / PETITIONER
**AND:**
**{judgment_debtor}**                                           ... JUDGMENT DEBTOR / RESPONDENT

---

## PETITION UNDER ORDER XXI RULE 11(2) READ WITH SECTION 36 OF THE ARBITRATION AND CONCILIATION ACT, 1996

1. **The {decree_nature}:** A {decree_nature.lower()} dated `{decree_date}` was passed in favour of the Decree Holder and against the Judgment Debtor for a sum of **INR {decretal_amount:,.2f}** together with interest and costs. Under Section 36 of the Arbitration and Conciliation Act, 1996, the award is enforceable in the same manner as a decree of the Court.{case_note}
2. **Amount Due:** Principal decretal amount of **INR {decretal_amount:,.2f}** remains wholly unsatisfied. Indicative post-award interest @9% p.a. aggregates to approximately **INR {interest_amount:,.2f}** (subject to the rate actually awarded).
3. **Mode of Execution Sought:** The Decree Holder seeks execution by way of: {mode}, under Order XXI Rules 11(2), 37, 41, 54 and 64 of the Code of Civil Procedure, 1908.
4. **Limitation:** This petition is filed within **12 years** from the date of the {decree_nature.lower()} as prescribed by Article 136 of the Schedule to the Limitation Act, 1963, and is therefore within time.
5. **Assets & Means Inquiry:** The Judgment Debtor be directed to disclose assets on affidavit (Order XXI Rule 41 CPC), and the properties detailed in the annexed schedule be attached and sold for satisfaction of the decretal amount.{commercial_note}

## PRAYER
It is therefore prayed that this Hon'ble Court be pleased to order execution of the {decree_nature.lower()} dated `{decree_date}` by {mode}, and grant such further relief as this Hon'ble Court deems fit, in the interests of justice.

**Advocate for the Decree Holder**
Place: Bengaluru
Date: {datetime.now().strftime('%d.%m.%Y')}
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Success] Execution Petition saved -> '{path}'")


def handle_execution_cli(args):
    p = argparse.ArgumentParser(prog="sweety legal execution")
    p.add_argument("--decree-holder", default="M/s. Apex Ventures Pvt. Ltd.")
    p.add_argument("--judgment-debtor", default="M/s. Orion Infra LLP")
    p.add_argument("--decree-date", default="2026-05-20")
    p.add_argument("--amount", type=float, default=2500000.0)
    p.add_argument("--mode", default="attachment and sale of movable/immovable property, and garnishee of bank accounts")
    p.add_argument("--decree-nature", default="Decree/Award")
    p.add_argument("--case-no", default=None, help="Suit/proceedings number out of which execution arises")
    p.add_argument("--commercial", action="store_true", help="Flag: underlying dispute is commercial")
    a = p.parse_args(args)
    generate_execution_petition(a.decree_holder, a.judgment_debtor, a.decree_date, a.amount, a.mode,
                                a.decree_nature, a.case_no, a.commercial)


if __name__ == "__main__":
    import sys
    handle_execution_cli(sys.argv[1:])
