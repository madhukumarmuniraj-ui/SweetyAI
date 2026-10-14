import os
import sys
import argparse
from datetime import datetime

OUTPUT_DIR = "hc_quashing_petitions"

def generate_hc_quashing_suite(
    petitioner,
    police_station,
    complainant,
    crime_no,
    cc_no,
    trial_court,
    offences,
    fir_date,
    mode="crlp528",
    civil_dispute=True,
    sec175_violation=True
):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if mode == "wp226":
        title_header = (
            "IN THE HIGH COURT OF KARNATAKA AT BENGALURU\n"
            "(ORIGINAL WRIT JURISDICTION)\n"
            "WRIT PETITION NO. _________ OF 2026 (GM-RES)"
        )
        provision_line = (
            "Articles 226 and 227 of the Constitution of India read with "
            "Section 528 of the Bharatiya Nagarik Suraksha Sanhita, 2023"
        )
    else:
        title_header = (
            "IN THE HIGH COURT OF KARNATAKA AT BENGALURU\n"
            "(MEMORANDUM OF CRIMINAL PETITION UNDER SECTION 528 OF THE BHARATIYA NAGARIK SURAKSHA SANHITA, 2023)\n"
            "CRIMINAL PETITION (CRL.P.) NO. _________ OF 2026"
        )
        provision_line = (
            "Section 528 of the Bharatiya Nagarik Suraksha Sanhita, 2023 "
            "(Corresponding to Section 482 of the Code of Criminal Procedure, 1973)"
        )

    target_proceeding = (
        f"FIR in {crime_no} dated {fir_date} registered by Respondent No. 1 ({police_station}) "
        f"and consequential proceedings in {cc_no} pending on the file of the learned {trial_court}"
        if cc_no != "N/A"
        else f"FIR in {crime_no} dated {fir_date} registered by Respondent No. 1 ({police_station}) pending on the file of the learned {trial_court}"
    )

    extra_grounds = ""
    if civil_dispute:
        extra_grounds += """
3. **Purely Civil / Commercial Dispute Given a Cloak of Criminality (*Indian Oil Corp. v. NEPC India Ltd.*, (2006) 6 SCC 736 & *G. Sagar Suri v. State of U.P.*, (2000) 2 SCC 636):**
   A bare perusal of the complaint and FIR reveals that the gravamen of the dispute arises out of an alleged breach of commercial/contractual obligations. For an offence of cheating under Section 318 BNS (formerly Section 420 IPC), fraudulent or dishonest intention must be shown to exist **at the very inception of the transaction** (*Hridaya Ranjan Prasad Verma v. State of Bihar*, (2000) 4 SCC 168). Mere subsequent failure to keep a commercial promise cannot criminalize a civil dispute, and the criminal justice machinery is being weaponized as an arm-twisting recovery mechanism.
"""
    if sec175_violation:
        extra_grounds += """
4. **Non-Compliance with Mandatory Safeguards under Sections 173(3) & 175(3) BNSS (*Priyanka Srivastava v. State of U.P.*, (2015) 6 SCC 287):**
   The registration of the impugned crime and referral for investigation suffer from incurable procedural illegality. Under **Section 175(3) of the BNSS, 2023**, no Magistrate can mechanically direct registration of an FIR without: (i) verifying prior compliance under Section 173(4) BNSS supported by a sworn affidavit per *Priyanka Srivastava*, (ii) considering the submissions of the Police Officer, and (iii) applying judicial mind via a reasoned speaking order. Furthermore, where the alleged offence carries a punishment between 3 and 7 years, **Section 173(3) BNSS** contemplates a preliminary inquiry to ascertain whether a prima facie case exists.
"""

    bundle = f"""# {title_header}

**IN THE MATTER OF:**
*{provision_line}*

**BETWEEN:**
**{petitioner}**                                                 ... PETITIONER / ACCUSED

**AND:**
1. **The State of Karnataka**
   By `{police_station}`,
   Represented by the State Public Prosecutor,
   High Court Building, Bengaluru - 560 001.

2. **{complainant}**                                             ... RESPONDENTS

---

## PART I: STATUTORY & BHAJAN LAL QUASHING AUDIT MATRIX
| Audit Gate | Controlling Statute / Supreme Court Precedent | Case Applicability |
| :--- | :--- | :--- |
| **Inherent / Writ Jurisdiction** | `{provision_line}` | Invoked to prevent abuse of process of Court & secure ends of justice |
| **Impugned Proceeding** | `{crime_no}` (`{cc_no}`) on the file of `{trial_court}` | Registered on `{fir_date}` under `{offences}` |
| **Bhajan Lal Prong (1) & (3)** | *State of Haryana v. Bhajan Lal*, 1992 Supp (1) SCC 335 | Uncontroverted allegations do not disclose essential ingredients of `{offences}` |
| **Bhajan Lal Prong (7)** | Mala fide & Ulterior Motive | Manifestly attended with mala fides to wreak vengeance / extort settlement |
| **Civil Cloaked as Criminal** | *G. Sagar Suri* (2000) 2 SCC 636; *Lalita Kumari* (2014) 2 SCC 1 | `{'YES — Contractual dispute lacking inception mens rea' if civil_dispute else 'Standard Evidentiary Challenge'}` |
| **Sec. 173(3) / 175(3) BNSS Gate** | *Priyanka Srivastava* (2015) 6 SCC 287 & Sec. 175(3) BNSS | `{'VIOLATED — Mandatory affidavit & police submission inquiry omitted' if sec175_violation else 'Standard FIR Registration Challenge'}` |

---

## PART II: SYNOPSIS & CHRONOLOGICAL LIST OF DATES
*(Prepared under Chapter XII of the High Court of Karnataka Rules, 1959)*

| Sl. No. | Date | Chronological Event |
| :--- | :--- | :--- |
| 1. | Prior to `{fir_date}` | Commercial / civil transactions transpired between the Petitioner and Respondent No. 2 without any dishonest inducement at inception. |
| 2. | `{fir_date}` | Respondent No. 2 lodged a motivated complaint culminating in `{crime_no}` by `{police_station}` for alleged offences under `{offences}`. |
| 3. | Subsequent | `{cc_no}` registered/pending before the learned `{trial_court}`, prompting the present Petition under `{provision_line}`. |

---

## PART III: MEMORANDUM OF PETITION UNDER SECTION 528 BNSS, 2023

The Petitioner above-named most respectfully submits as follows:
1. The Petitioner is approaching this Hon'ble Court invoking its inherent jurisdiction under **{provision_line}**, seeking to quash the **{target_proceeding}** for the alleged offences punishable under **{offences}**.

### GROUNDS FOR QUASHING
1. **Squarely Covered by Parameters (1), (3), (5) and (7) of *State of Haryana v. Bhajan Lal*, 1992 Supp (1) SCC 335:**
   Even if the allegations made in the First Information Report / Complaint are taken at their face value and accepted in their entirety, they do not *prima facie* constitute any offence or make out a case against the Petitioner under **{offences}**.
2. **Absence of Essential Statutory Ingredients (*Mahmood Ali v. State of U.P.*, 2023 INSC 684):**
   As held by the Hon'ble Supreme Court in *Mahmood Ali v. State of U.P.*, while exercising jurisdiction under Section 528 BNSS (formerly Section 482 Cr.P.C.), the High Court has a duty to read between the lines and look beyond clever drafting to see whether the criminal proceeding is manifestly frivolous or vexatious.
{extra_grounds}

### MAIN PRAYER
WHEREFORE, the Petitioner most respectfully prays that this Hon'ble Court may be pleased to:
(a) Call for the relevant records in **{crime_no}** (`{cc_no}`) on the file of the learned **{trial_court}**;
(b) **QUASH** the entire proceedings in **{target_proceeding}** for the offences punishable under **{offences}**, insofar as the Petitioner is concerned; and
(c) Pass such other order or direction as this Hon'ble Court deems fit in the facts and circumstances of the case, in the interest of justice and equity.

---

## PART IV: I.A. NO. 1/2026 FOR INTERIM STAY OF FURTHER PROCEEDINGS
*(Under Section 528 of the Bharatiya Nagarik Suraksha Sanhita, 2023)*

1. For the reasons stated in the accompanying Memorandum of Petition and Affidavit, the continuation of investigation / trial proceedings in **{crime_no}** (`{cc_no}`) operates as a grave abuse of the process of law and infringes the Petitioner's fundamental right to personal liberty under Article 21 of the Constitution.
2. **Compliance with *Neeharika Infrastructure Pvt. Ltd. v. State of Maharashtra*, (2021) 19 SCC 401:** This is an exceptional case where the uncontroverted allegations ex-facie fail to disclose the commission of any cognizable offence, warranting an ad-interim order of stay for reasons recorded.

### INTERIM PRAYER
WHEREFORE, the Petitioner prays that this Hon'ble Court may be pleased to **STAY all further investigation and proceedings** in **{target_proceeding}** pending disposal of the main Petition, in the interest of justice and equity.
"""

    safe_cr = "".join(c if c.isalnum() else "_" for c in crime_no)
    out_path = os.path.join(OUTPUT_DIR, f"hc_quash_{mode}_{safe_cr}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(bundle)

    print(bundle)
    print(f"\n[Success] High Court Sec. 528 BNSS Quashing / Writ Bundle saved -> '{out_path}'")
    return out_path

def handle_hc_quash_cli(argv):
    p = argparse.ArgumentParser(prog="sweety legal hc-quash")
    p.add_argument("--petitioner", default="Sri. Petitioner / Accused No. 1")
    p.add_argument("--ps", default="Whitefield Police Station, Bengaluru")
    p.add_argument("--complainant", default="Sri. Defacto Complainant")
    p.add_argument("--crime-no", required=True, help="e.g. Crime No. 312/2026")
    p.add_argument("--cc-no", default="C.C. No. 22410/2026", help="Trial Court CC/Spl.C No. or N/A")
    p.add_argument("--trial-court", default="IV Addl. Chief Judicial Magistrate (ACJM), Bengaluru")
    p.add_argument("--offences", default="Sections 316(2) and 318(4) of the Bharatiya Nyaya Sanhita, 2023")
    p.add_argument("--fir-date", required=True, help="YYYY-MM-DD")
    p.add_argument("--mode", choices=["crlp528", "wp226"], default="crlp528", help="crlp528 or wp226")
    p.add_argument("--no-civil", action="store_true", help="Omit civil-dispute ground")
    p.add_argument("--no-175", action="store_true", help="Omit Sec. 173(3)/175(3) BNSS ground")
    a = p.parse_args(argv)
    generate_hc_quashing_suite(
        a.petitioner, a.ps, a.complainant, a.crime_no, a.cc_no,
        a.trial_court, a.offences, a.fir_date, a.mode,
        not a.no_civil, not a.no_175
    )

if __name__ == "__main__":
    if len(sys.argv) > 1:
        handle_hc_quash_cli(sys.argv[1:])
