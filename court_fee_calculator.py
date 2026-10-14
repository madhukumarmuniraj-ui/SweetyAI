import os
import sys
import math
import datetime
import argparse

VALUATION_DIR = "valuation_slips"

# Schedule I, Article 1 of the Karnataka Court-Fees and Suits Valuation Act, 1958
# (Substituted by Karnataka Act 2 of 1993) - 16 Progressive Slabs
# Format: (lower_threshold, upper_limit, base_fee, marginal_rate_percent)
KARNATAKA_SLABS = [
    (0, 15000, 0.0, 2.5),
    (15000, 75000, 375.0, 7.5),
    (75000, 250000, 4875.0, 7.0),
    (250000, 500000, 17125.0, 6.5),
    (500000, 750000, 33375.0, 6.0),
    (750000, 1000000, 48375.0, 5.5),
    (1000000, 1500000, 62125.0, 5.0),
    (1500000, 2000000, 87125.0, 4.5),
    (2000000, 2500000, 109625.0, 4.0),
    (2500000, 3000000, 129625.0, 3.5),
    (3000000, 4000000, 147125.0, 3.0),
    (4000000, 5000000, 177125.0, 2.5),
    (5000000, 6000000, 202125.0, 2.0),
    (6000000, 7000000, 222125.0, 1.5),
    (7000000, 8000000, 237125.0, 1.0),
    (8000000, float("inf"), 247125.0, 0.5),
]

SUIT_CATEGORIES = {
    "money": {
        "title": "Suit for Money / Recovery / Damages",
        "section": "Section 21 read with Schedule I, Article 1 of KCFSV Act, 1958",
        "mode": "ad_valorem_full",
        "limitation_days": 1095,  # 3 years
        "limitation_years": 3,
        "limitation_art": "Articles 14 / 19 / 55 of the Limitation Act, 1963 (3 Years)",
        "sec5_applicable": False,
    },
    "commercial": {
        "title": "Commercial Dispute Suit (Commercial Courts Act, 2015)",
        "section": "Section 21 KCFSV Act read with Section 2(1)(i) & Section 12A Commercial Courts Act, 2015",
        "mode": "commercial_full",
        "limitation_days": 1095,
        "limitation_years": 3,
        "limitation_art": "Article 55 / 113 Limitation Act, 1963 + Sec. 12A(3) PIM exclusion",
        "sec5_applicable": False,
    },
    "specific_performance": {
        "title": "Suit for Specific Performance of Contract",
        "section": "Section 40(a) read with Schedule I, Article 1 of KCFSV Act, 1958",
        "mode": "ad_valorem_full",
        "limitation_days": 1095,
        "limitation_years": 3,
        "limitation_art": "Article 54 of the Limitation Act, 1963 (3 Years from date fixed or refusal)",
        "sec5_applicable": False,
    },
    "declaration_possession": {
        "title": "Suit for Declaration of Title & Possession",
        "section": "Section 24(a) read with Schedule I, Article 1 of KCFSV Act, 1958",
        "mode": "ad_valorem_min_1000",
        "limitation_days": 4380,
        "limitation_years": 12,
        "limitation_art": "Article 65 of the Limitation Act, 1963 (12 Years for possession based on title)",
        "sec5_applicable": False,
    },
    "declaration_injunction": {
        "title": "Suit for Declaration with Consequential Injunction (Immovable Property)",
        "section": "Section 24(b) read with Schedule I, Article 1 of KCFSV Act, 1958",
        "mode": "ad_valorem_half_min_1000",
        "limitation_days": 1095,
        "limitation_years": 3,
        "limitation_art": "Article 58 of the Limitation Act, 1963 (3 Years when right to sue first accrues)",
        "sec5_applicable": False,
    },
    "injunction_title_denied": {
        "title": "Suit for Injunction where Title is Denied",
        "section": "Section 26(a) read with Schedule I, Article 1 of KCFSV Act, 1958",
        "mode": "ad_valorem_half_min_1000",
        "limitation_days": 1095,
        "limitation_years": 3,
        "limitation_art": "Article 113 of the Limitation Act, 1963 (3 Years)",
        "sec5_applicable": False,
    },
    "injunction_bare": {
        "title": "Suit for Bare Perpetual / Mandatory Injunction",
        "section": "Section 26(c) read with Schedule I, Article 1 of KCFSV Act, 1958",
        "mode": "fixed_min_1000",
        "limitation_days": 1095,
        "limitation_years": 3,
        "limitation_art": "Article 113 of the Limitation Act, 1963 (3 Years)",
        "sec5_applicable": False,
    },
    "partition_joint": {
        "title": "Suit for Partition & Separate Possession (Joint Possession)",
        "section": "Section 35(2) of KCFSV Act, 1958",
        "mode": "fixed_200",
        "limitation_days": 4380,
        "limitation_years": 12,
        "limitation_art": "Article 110 of the Limitation Act, 1963 (12 Years when exclusion becomes known)",
        "sec5_applicable": False,
    },
    "partition_excluded": {
        "title": "Suit for Partition (Plaintiff Excluded from Possession)",
        "section": "Section 35(1) read with Schedule I, Article 1 of KCFSV Act, 1958",
        "mode": "ad_valorem_full",
        "limitation_days": 4380,
        "limitation_years": 12,
        "limitation_art": "Article 110 of the Limitation Act, 1963 (12 Years when exclusion becomes known)",
        "sec5_applicable": False,
    },
    "arbitration_34": {
        "title": "Petition to Set Aside Arbitral Award (Section 34 A&C Act, 1996)",
        "section": "Schedule II, Article 11(n) of KCFSV Act, 1958",
        "mode": "fixed_arbitration",
        "limitation_days": 90,
        "limitation_years": 0,
        "limitation_art": "Section 34(3) Arbitration & Conciliation Act, 1996 (3 Months + max 30 days strict cap)",
        "sec5_applicable": False,
    },
    "writ": {
        "title": "Writ Petition before the High Court of Karnataka (Art. 226 / 227)",
        "section": "Schedule II, Article 1(d)(ii) of KCFSV Act, 1958",
        "mode": "fixed_100",
        "limitation_days": 0,
        "limitation_years": 0,
        "limitation_art": "Doctrine of Delay & Laches (No fixed period under Limitation Act; file promptly)",
        "sec5_applicable": True,
    },
    "rfa": {
        "title": "Regular First Appeal (RFA) before High Court of Karnataka",
        "section": "Section 49 read with Schedule I, Article 1 of KCFSV Act, 1958",
        "mode": "ad_valorem_full",
        "limitation_days": 90,
        "limitation_years": 0,
        "limitation_art": "Article 116(a) of the Limitation Act, 1963 (90 Days from date of decree)",
        "sec5_applicable": True,
    },
}


def compute_ad_valorem_karnataka(taxable_value):
    if taxable_value <= 0:
        return 0.0, "Zero valuation"
    for low, high, base, rate in KARNATAKA_SLABS:
        if taxable_value <= high:
            excess = taxable_value - low
            fee = base + (excess * (rate / 100.0))
            slab_desc = (
                f"Slab: Above INR {low:,.0f} up to INR {high:,.0f} "
                f"(Base INR {base:,.2f} + {rate}% on INR {excess:,.2f})"
                if high != float("inf")
                else f"Slab: Above INR {low:,.0f} (Base INR {base:,.2f} + {rate}% on INR {excess:,.2f})"
            )
            return math.ceil(fee), slab_desc
    return 0.0, "Out of range"


def add_years_safe(d, years):
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d.replace(year=d.year + years, day=28)


def run_calculation(suit_type, claim_value, cause_date_str=None, exclusion_days=0, petitioners=1):
    os.makedirs(VALUATION_DIR, exist_ok=True)
    info = SUIT_CATEGORIES.get(suit_type)
    if not info:
        print(f"[Error] Unknown category '{suit_type}'. Available: {', '.join(SUIT_CATEGORIES.keys())}")
        return

    mode = info["mode"]
    notes = []

    if mode == "ad_valorem_full":
        computable_value = max(claim_value, 1000.0)
        fee, breakdown = compute_ad_valorem_karnataka(computable_value)
    elif mode == "commercial_full":
        computable_value = max(claim_value, 1000.0)
        fee, breakdown = compute_ad_valorem_karnataka(computable_value)
        if claim_value < 300000:
            notes.append(
                "CRITICAL JURISDICTION WARNING: Claim value is below INR 3,00,000. "
                "Section 2(1)(i) of the Commercial Courts Act, 2015 requires a 'Specified Value' "
                "of not less than INR 3,00,000 for Commercial Court jurisdiction."
            )
        else:
            notes.append(
                "COMMERCIAL COURT COMPLIANCE: Meets Specified Value threshold (>= INR 3,00,000). "
                "Ensure Statement of Truth (Order XI Rule 1 CPC as amended) and Section 12A "
                "Pre-Institution Mediation compliance (unless urgent interim relief is sought)."
            )
    elif mode == "ad_valorem_min_1000":
        computable_value = max(claim_value, 1000.0)
        fee, breakdown = compute_ad_valorem_karnataka(computable_value)
    elif mode == "ad_valorem_half_min_1000":
        computable_value = max(claim_value * 0.5, 1000.0)
        fee, breakdown = compute_ad_valorem_karnataka(computable_value)
        notes.append(
            f"Statutory 50% Valuation Applied: Market value INR {claim_value:,.2f} "
            f"valued at one-half = INR {computable_value:,.2f} for court fee computation."
        )
    elif mode == "fixed_min_1000":
        computable_value = 1000.0
        fee, breakdown = compute_ad_valorem_karnataka(computable_value)
        notes.append(f"Valued at statutory minimum of INR 1,000 per relief -> Court Fee INR {fee:,.2f}.")
    elif mode == "fixed_200":
        computable_value = claim_value
        fee = 200.0 * max(1, petitioners)
        breakdown = "Fixed Court Fee of INR 200 (Joint Possession in Civil / Senior Civil Judge Court)"
    elif mode == "fixed_100":
        computable_value = claim_value
        fee = 100.0 * max(1, petitioners)
        breakdown = f"Fixed Court Fee of INR 100 x {petitioners} Petitioner(s) (High Court Writ Jurisdiction)"
    elif mode == "fixed_arbitration":
        computable_value = claim_value
        fee = 100.0 if claim_value > 5000 else 25.0
        breakdown = "Schedule II, Article 11(n) KCFSV Act fixed fee on arbitral award challenge"
    else:
        computable_value = claim_value
        fee, breakdown = compute_ad_valorem_karnataka(computable_value)

    # Limitation Period Calculation
    today = datetime.date.today()
    limitation_report = "No cause-of-action date provided (pass --cause-date YYYY-MM-DD to audit limitation)."
    if cause_date_str:
        try:
            cause_date = datetime.datetime.strptime(cause_date_str, "%Y-%m-%d").date()
            if info["limitation_years"] > 0:
                base_expiry = add_years_safe(cause_date, info["limitation_years"])
            elif info["limitation_days"] > 0:
                base_expiry = cause_date + datetime.timedelta(days=info["limitation_days"])
            else:
                base_expiry = None

            if base_expiry:
                final_expiry = base_expiry + datetime.timedelta(days=exclusion_days)
                days_remaining = (final_expiry - today).days
                status = (
                    f"WITHIN LIMITATION ({days_remaining} days remaining)"
                    if days_remaining >= 0
                    else f"BARRED BY LIMITATION (Expired {abs(days_remaining)} days ago)"
                )
                condonation_note = (
                    "Section 5 Limitation Act condonation applies ONLY to appeals/applications (NOT original suits)."
                    if not info["sec5_applicable"] and suit_type != "arbitration_34"
                    else (
                        "STRICT PROVISO TO SEC. 34(3) A&C ACT: Delay condonable up to max 30 days beyond 3 months; "
                        "Section 5 Limitation Act is excluded thereafter (Simplex Infrastructure v. Union of India)."
                        if suit_type == "arbitration_34"
                        else "Section 5 Limitation Act condonation of delay available upon showing 'sufficient cause'."
                    )
                )
                limitation_report = (
                    f"- **Date of Accrual / Impugned Order:** {cause_date.strftime('%d-%m-%Y')}\n"
                    f"- **Statutory Period:** {info['limitation_art']}\n"
                    f"- **Section 12 / 12A Excluded Days:** {exclusion_days} day(s)\n"
                    f"- **Last Date for Filing:** {final_expiry.strftime('%d-%m-%Y')}\n"
                    f"- **Limitation Status (as of {today.strftime('%d-%m-%Y')}):** `{status}`\n"
                    f"- **Condonation Rule:** {condonation_note}"
                )
            else:
                Elapsed = (today - cause_date).days
                limitation_report = (
                    f"- **Date of Impugned Action:** {cause_date.strftime('%d-%m-%Y')} ({Elapsed} days elapsed)\n"
                    f"- **Governing Rule:** {info['limitation_art']}"
                )
        except ValueError:
            limitation_report = f"[Error] Invalid date format '{cause_date_str}'. Use YYYY-MM-DD."

    slip_md = f"""# IN THE COURT OF THE PRINCIPAL CITY CIVIL AND SESSIONS JUDGE / HIGH COURT OF KARNATAKA AT BENGALURU

## VALUATION SLIP & STATUTORY LIMITATION AUDIT
*(Prepared under Section 10 of the Karnataka Court-Fees and Suits Valuation Act, 1958)*

| Particular | Statutory Computation |
| :--- | :--- |
| **Nature of Proceeding** | {info['title']} |
| **Governing Provision** | {info['section']} |
| **Gross Claim / Market Value** | INR {claim_value:,.2f} |
| **Valued at (for Court Fee)** | INR {computable_value:,.2f} |
| **Slab / Fee Computation** | {breakdown} |
| **TOTAL COURT FEE PAYABLE** | **INR {fee:,.2f}** |
| **Settlement Refund Eligibility** | **100% Refundable** (INR {fee:,.2f}) under Section 66 KCFSV Act (as amended by Act 21 of 2020) upon settlement via ADR / Lok Adalat / Mediation |

---

## II. LIMITATION PERIOD AUDIT
{limitation_report}

---

## III. PRACTICE & COMPLIANCE NOTES
"""
    if notes:
        for n in notes:
            slip_md += f"- {n}\n"
    else:
        slip_md += "- Payment permitted via e-Payment / Khajane-II portal under Section 71 of the KCFSV Act, 1958.\n"

    out_path = os.path.join(VALUATION_DIR, f"valuation_slip_{suit_type}_{int(claim_value)}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(slip_md)

    print("\n" + slip_md)
    print("=========================================================================")
    print(f"[Success] Court Fee Valuation Slip saved to -> '{out_path}'")
    print("          (Run `python3 sweety.py export " + out_path + "` for A4 Court-Ready HTML)")
    print("=========================================================================\n")


def handle_calc_cli(argv):
    parser = argparse.ArgumentParser(
        prog="sweety calc-fees",
        description="Karnataka Court Fees & Statutory Limitation Calculator (KCFSV Act, 1958)",
    )
    parser.add_argument(
        "--type",
        choices=list(SUIT_CATEGORIES.keys()),
        default="money",
        help="Category of suit, appeal, or petition",
    )
    parser.add_argument(
        "--value",
        type=float,
        default=0.0,
        help="Market value or claim amount in INR",
    )
    parser.add_argument(
        "--cause-date",
        type=str,
        default=None,
        help="Date cause of action accrued or order passed (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--exclusion-days",
        type=int,
        default=0,
        help="Days excluded under Sec. 12 Limitation Act (certified copy) or Sec. 12A PIM",
    )
    parser.add_argument(
        "--petitioners",
        type=int,
        default=1,
        help="Number of petitioners/shares (for writ or partition_joint)",
    )
    args = parser.parse_args(argv)
    run_calculation(args.type, args.value, args.cause_date, args.exclusion_days, args.petitioners)


if __name__ == "__main__":
    handle_calc_cli(sys.argv[1:])
