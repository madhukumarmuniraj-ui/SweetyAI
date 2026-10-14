import os
import sys
import argparse

OUTPUT_DIR = "stamp_duty_reports"

# Karnataka Stamp Act Rates (Including Act 04 of 2024 Amendments)
STAMP_RATES_2024 = {
    "conveyance_urban": {"stamp_pct": 5.0, "surcharge_pct": 2.0, "cess_pct": 10.0, "reg_pct": 1.0},
    "conveyance_rural": {"stamp_pct": 5.0, "surcharge_pct": 3.0, "cess_pct": 10.0, "reg_pct": 1.0},
    "lease_deed": {"stamp_pct": 1.0, "reg_pct": 1.0, "desc": "1% of average annual rent / premium"},
    "leave_and_license": {"stamp_pct": 0.5, "reg_pct": 0.5, "desc": "0.5% of total license fee + security deposit"},
    "mortgage_with_possession": {"stamp_pct": 5.0, "reg_pct": 1.0},
    "modt_eqm": {"stamp_pct": 0.5, "min_stamp": 500.0, "desc": "0.5% of loan amount (No upper cap post-2024)"},
    "hypothecation": {"stamp_pct": 0.5, "min_stamp": 500.0, "desc": "0.5% of loan amount"},
    "agreement_general": {"fixed_stamp": 500.0, "desc": "Article 5(j) revised to INR 500"},
    "affidavit": {"fixed_stamp": 100.0, "desc": "Article 4 revised to INR 100"},
    "spa": {"fixed_stamp": 500.0, "desc": "Special Power of Attorney Article 41"},
    "gpa": {"fixed_stamp": 1000.0, "desc": "General Power of Attorney Article 41"},
    "indemnity_bond": {"stamp_pct": 0.2, "min_stamp": 500.0, "desc": "0.2% above 10 Lakhs"},
}

def calculate_stamp_duty(instrument, value, location="urban", deficit_paid=0.0):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    stamp_duty = 0.0
    reg_fee = 0.0
    surcharge = 0.0
    cess = 0.0
    details = ""

    if instrument in ("conveyance_urban", "conveyance_rural"):
        rates = STAMP_RATES_2024[instrument]
        base_stamp = value * (rates["stamp_pct"] / 100.0)
        surcharge = base_stamp * (rates["surcharge_pct"] / 100.0)
        cess = base_stamp * (rates["cess_pct"] / 100.0)
        stamp_duty = base_stamp + surcharge + cess
        reg_fee = value * (rates["reg_pct"] / 100.0)
        details = f"Conveyance / Sale Deed ({location.upper()}): Base 5% + {rates['surcharge_pct']}% Surcharge + {rates['cess_pct']}% Cess"

    elif instrument == "modt_eqm":
        stamp_duty = max(500.0, value * 0.005)
        reg_fee = min(20000.0, value * 0.005)
        details = "Deposit of Title Deeds (MODT / EQM) under Karnataka Act 04 of 2024 (0.5% flat, cap removed)"

    elif instrument in STAMP_RATES_2024 and "fixed_stamp" in STAMP_RATES_2024[instrument]:
        stamp_duty = STAMP_RATES_2024[instrument]["fixed_stamp"]
        reg_fee = 200.0
        details = STAMP_RATES_2024[instrument]["desc"]

    else:
        stamp_duty = max(500.0, value * 0.01)
        reg_fee = 500.0
        details = "Standard General Instrument Calculation"

    total_payable = stamp_duty + reg_fee
    
    # Sections 33 & 34 Impounding Penalty (Deficient Duty + 10x Penalty)
    deficient = max(0.0, stamp_duty - deficit_paid)
    impounding_penalty = deficient * 10.0 if deficient > 0 else 0.0
    total_with_penalty = total_payable + impounding_penalty

    report = f"""# KARNATAKA STAMP DUTY, REGISTRATION & IMPOUNDING AUDIT
*(Computed under the Karnataka Stamp Act, 1957 as amended by Karnataka Act No. 04 of 2024)*

| Parameter | Value / Calculation |
| :--- | :--- |
| **Instrument Type** | `{instrument}` |
| **Consideration / Market Value** | **INR {value:,.2f}** |
| **Statutory Basis** | {details} |
| **Calculated Stamp Duty** | **INR {stamp_duty:,.2f}** |
| **Registration Fee** | **INR {reg_fee:,.2f}** |
| **Total Statutory Payable** | **INR {total_payable:,.2f}** |
| **Deficient Stamp Duty Paid** | INR {deficit_paid:,.2f} |
| **Sec. 33/34 Impounding Penalty (10x)** | **INR {impounding_penalty:,.2f}** |
| **TOTAL PAYABLE WITH PENALTY** | **INR {total_with_penalty:,.2f}** |

> **Legal Note under Sec. 34 Karnataka Stamp Act:** No instrument chargeable with duty shall be admitted in evidence for any purpose by any person having by law consent to receive evidence, or shall be acted upon, unless such instrument is duly stamped.
"""

    out_path = os.path.join(OUTPUT_DIR, f"stamp_audit_{instrument}_{int(value)}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print(f"\n[Success] Stamp Duty & Impounding Report saved -> '{out_path}'")
    return out_path

def handle_stamp_cli(argv):
    p = argparse.ArgumentParser(prog="sweety legal stamp-duty")
    p.add_argument("--instrument", required=True, choices=list(STAMP_RATES_2024.keys()))
    p.add_argument("--value", type=float, required=True, help="Market value or consideration amount in INR")
    p.add_argument("--location", default="urban", choices=["urban", "rural"])
    p.add_argument("--deficit", type=float, default=0.0, help="Deficient stamp duty already paid (for Sec. 33/34 penalty)")
    a = p.parse_args(argv)
    calculate_stamp_duty(a.instrument, a.value, a.location, a.deficit)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        handle_stamp_cli(sys.argv[1:])
