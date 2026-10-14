import os
import sys
import subprocess

def write_clean(filename, content):
    cleaned = content.replace("\u00a0", " ").replace("\u200b", "")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(cleaned)

FILING_FORMS_CODE = r'''import os
import sys
import argparse
from datetime import datetime

def _safe_name(name):
    return "".join(c if c.isalnum() else "_" for c in name)

def generate_vakalatnama(court_name, case_no, client_name, opponent_name, advocate_name="Madhukumar Muniraj", bar_reg="KAR/______/202"):
    os.makedirs("filing_forms", exist_ok=True)
    safe_client = _safe_name(client_name)
    path = f"filing_forms/vakalatnama_{safe_client}.md"
    content = f"""# IN {court_name.upper()}
## {case_no}

**BETWEEN:**
**{client_name}**                                                  ... PLAINTIFF / PETITIONER / APPELLANT
**VERSUS**
**{opponent_name}**                                                 ... DEFENDANT / RESPONDENT

---
## VAKALATNAMA
KNOW ALL men by these presents that I/We, **{client_name}**, the above-named party, do hereby appoint and retain:

**{advocate_name}**
Advocate (Enrollment No. `{bar_reg}`)
Chambers: Bengaluru, Karnataka

To appear, plead, and act for me/us in the above--noted case and in all proceedings arising therefrom, including appeals, revisions, execution petitions, and applications for review.
1. I/We authorize the Advocate to engage other counsel if necessary, to withdraw or compromise the matter, and to receive money on my/our behalf.
2. I/We agree to pay the professional fees agreed upon.

**ACCEPTED & FILED BY:**


_________________________________
**({advocate_name})**
Advocate


_________________________________
**({client_name})**
Client / Executant
**DATE:** {datetime.now().strftime('%d-%m-%Y')}
**PLACE:** Bengaluru
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Success] Vakalatnama saved -> '{path}'")

def generate_memo_of_appearance(court_name, case_no, client_name, opponent_name, advocate_name="Madhukumar Muniraj", bar_reg="KAR/______/202"):
    os.makedirs("filing_forms", exist_ok=True)
    safe_client = _safe_name(client_name)
    path = f"filing_forms/memo_of_appearance_{safe_client}.md"
    content = f"""# IN {court_name.upper()}
## {case_no}

**BETWEEN:**
**{client_name}**                                                  ... PLAINTIFF / PETITIONER
**VERSUS**
**{opponent_name}**                                                 ... DEFENDANT / RESPONDENT

---
## MEMO OF APPEARANCE
The undersigned enters appearance on behalf of the **{client_name}** in the above-noted matter. 

1. Copies of plaints, petitions, applications, and court notices may henceforth be served upon the undersigned at the address given below.
2. Vakalatnama executed in favor of the undersigned is being filed / shall be filed within the statutory period.

**BENGALURU**
**DATE:** {datetime.now().strftime('%d-%m-%Y')}


_________________________________
**({advocate_name})**
Advocate (Enrollment No. `{bar_reg}`)
Chambers: Bengaluru, Karnataka
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Success] Memo of Appearance saved -> '{path}'")

def generate_pf_memo(court_name, case_no, plaintiff_name, defendant_name, num_defendants=1, claim_amount=1000000.0):
    os.makedirs("filing_forms", exist_ok=True)
    safe_client = _safe_name(plaintiff_name)
    path = f"filing_forms/process_fee_memo_{safe_client}.md"
    
    # Karnataka Process Fee Calculation (Standard Scale)
    pf_per_defendant = 50.0
    postal_charges = 45.0 * num_defendants
    total_pf = (pf_per_defendant * num_defendants) + postal_charges

    content = f"""# IN {court_name.upper()}
## {case_no}

**BETWEEN:**
**{plaintiff_name}**                                                ... PLAINTIFF
**VERSUS**
**{defendant_name}**                                                ... DEFENDANT

---
## MEMORANDUM OF PROCESS FEE (PF) & POSTAL CHARGES
The Plaintiff respectfully submits the following Process Fee calculation and postal charges for issuance of summons / notices to the Defendant(s) via Registered Post Acknowledgement Due (RPAD) and Court Process Server:

| Sl. No. | Particulars / Head of Charge | Rate (INR) | Quantity / Defendants | Total Amount (INR) |
| :--- | :--- | :--- | :--- | :--- |
| **1.** | Court Process Fee (Summons / Notice) | ₹50.00 | {num_defendants} Defendant(s) | ₹{pf_per_defendant * num_defendants:,.2f} |
| **2.** | Postal Charges (RPAD with Acknowledgment) | ₹45.00 | {num_defendants} Cover(s) | ₹{postal_charges:,.2f} |
| **3.** | Copying & Miscellaneous Service Charges | ₹25.00 | Lump sum | ₹25.00 |
| **TOTAL** | **payable via Court Fee Stamp / e-Chalan** | | | **₹{total_pf + 25.00:,.2f}** |

**BENGALURU**
**DATE:** {datetime.now().strftime('%d-%m-%Y')}


_________________________________
**ADVOCATE FOR THE PLAINTIFF**
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Success] Process Fee Memo saved -> '{path}'")

def handle_forms_cli(args):
    p = argparse.ArgumentParser(prog="sweety legal forms")
    p.add_argument("form_type", choices=["vakalatnama", "appearance", "pf-memo"], default="vakalatnama", nargs="?")
    p.add_argument("--court", default="THE CITY CIVIL & SESSIONS COURT AT BENGALURU (CCH-83)")
    p.add_argument("--caseno", default="Com.O.S. NO. _________ OF 2026")
    p.add_argument("--client", default="M/s. Apex Precision Tech")
    p.add_argument("--opponent", default="M/s. Zenith Logistics Corp")
    p.add_argument("--defendants", type=int, default=1)
    p.add_argument("--amount", type=float, default=2500000.0)
    
    a = p.parse_args(args)
    if a.form_type == "vakalatnama":
        generate_vakalatnama(a.court, a.caseno, a.client, a.opponent)
    elif a.form_type == "appearance":
        generate_memo_of_appearance(a.court, a.caseno, a.client, a.opponent)
    elif a.form_type == "pf-memo":
        generate_pf_memo(a.court, a.caseno, a.client, a.opponent, num_defendants=a.defendants, claim_amount=a.amount)
'''

write_clean("filing_forms.py", FILING_FORMS_CODE)

with open("sweety.py", "r", encoding="utf-8") as f:
    router_code = f.read().replace("\u00a0", " ").replace("\u200b", "")

forms_route = '''        # Module 39: Filing Forms Suite (Vakalatnama, Appearance & Process Fee Memo)
        if _cmd in ("forms", "vakalatnama", "pf-memo") or (_cmd == "legal" and _sub in ("forms", "vakalatnama", "pf-memo")):
            from filing_forms import handle_forms_cli
            _args = _sys.argv[2:] if _cmd in ("forms", "vakalatnama", "pf-memo") else _sys.argv[3:]
            handle_forms_cli(_args)
            _sys.exit(0)

'''

if "filing_forms" not in router_code:
    target = "        # Mobile Web Portal"
    router_code = router_code.replace(target, forms_route + target)
    write_clean("sweety.py", router_code)

for fname in ("filing_forms.py", "sweety.py"):
    with open(fname, "rb") as f:
        compile(f.read(), fname, "exec")
print("[Compile Check] filing_forms.py and sweety.py compiled cleanly with 0 errors!")

subprocess.run(["python3", "sweety.py", "legal", "forms", "vakalatnama"], check=True)
subprocess.run(["python3", "sweety.py", "legal", "forms", "appearance"], check=True)
subprocess.run(["python3", "sweety.py", "legal", "forms", "pf-memo"], check=True)
