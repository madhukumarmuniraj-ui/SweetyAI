import os
import sys
import re
import zipfile
import datetime
import argparse
import xml.etree.ElementTree as ET

BAIL_OUT_DIR = "bail_petitions"
DOWNLOADS_DIR = os.path.expanduser("~/Downloads")
DOC_EXTENSIONS = (".pdf", ".docx", ".md", ".txt", ".doc", ".rtf")

FORUM_CONFIG = {
    "hc": {
        "court_header": "IN THE HIGH COURT OF KARNATAKA AT BENGALURU",
        "jurisdiction_title": "(ORIGINAL CRIMINAL JURISDICTION)",
        "case_prefix": "CRL.P. No. ____________ / 2026",
        "respondent_desc": "State of Karnataka,\nBy {ps},\nRepresented by the State Public Prosecutor,\nHigh Court Building, Bengaluru – 560 001.",
        "court_short": "Hon'ble High Court of Karnataka",
    },
    "sessions": {
        "court_header": "IN THE COURT OF THE PRINCIPAL CITY CIVIL AND SESSIONS JUDGE AT BENGALURU (CCH-1)",
        "jurisdiction_title": "(CRIMINAL MISCELLANEOUS JURISDICTION)",
        "case_prefix": "CRL. MISC. No. ____________ / 2026",
        "respondent_desc": "State of Karnataka,\nBy {ps},\nRepresented by the learned Public Prosecutor,\nCity Civil Court Complex, Bengaluru – 560 009.",
        "court_short": "Hon'ble Court of Session",
    },
    "magistrate": {
        "court_header": "IN THE COURT OF THE ADDITIONAL CHIEF JUDICIAL MAGISTRATE (ACJM) AT BENGALURU",
        "jurisdiction_title": "(CRIMINAL JURISDICTION)",
        "case_prefix": "CRIMINAL MISC. / APPLICATION IN {crime_no}",
        "respondent_desc": "State of Karnataka,\nBy {ps},\nRepresented by the learned Senior Assistant Public Prosecutor,\nBengaluru.",
        "court_short": "Hon'ble Court",
    },
}


def extract_text_from_file(file_path):
    if not file_path or not os.path.exists(file_path):
        return ""
    ext = os.path.splitext(file_path)[1].lower()
    chunks = []
    if ext == ".docx" and zipfile.is_zipfile(file_path):
        try:
            with zipfile.ZipFile(file_path, "r") as z:
                if "word/document.xml" in z.namelist():
                    root = ET.fromstring(z.read("word/document.xml"))
                    for p in root.iter():
                        if p.tag.endswith("}p"):
                            runs = [t.text for t in p.iter() if t.tag.endswith("}t") and t.text]
                            if runs:
                                chunks.append("".join(runs))
        except Exception:
            pass
    elif ext == ".pdf":
        try:
            try:
                import pymupdf as fitz
            except ImportError:
                import fitz
            doc = fitz.open(file_path)
            for page in doc:
                chunks.append(page.get_text())
            doc.close()
        except Exception:
            pass
    text = "\n".join(chunks)
    if not text.strip():
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    return text.strip()


def get_latest_download():
    if not os.path.exists(DOWNLOADS_DIR):
        return None
    files = [
        os.path.join(DOWNLOADS_DIR, f)
        for f in os.listdir(DOWNLOADS_DIR)
        if os.path.isfile(os.path.join(DOWNLOADS_DIR, f)) and not f.startswith(".")
    ]
    doc_files = [f for f in files if os.path.splitext(f)[1].lower() in DOC_EXTENSIONS]
    target = doc_files if doc_files else files
    if not target:
        return None
    target.sort(key=os.path.getmtime, reverse=True)
    return target[0]


def check_statutory_bars_and_notices(bail_type, offences_str):
    alerts = []
    # Check for Section 65 or Section 70(2) BNS bar under Sec. 482(4) BNSS / notice under Sec. 483(2) BNSS
    has_sec65_or_70 = re.search(r"\b(65|70\(2\)|70)\b", offences_str)
    if has_sec65_or_70:
        if bail_type == "482":
            alerts.append(
                "CRITICAL STATUTORY BAR ALERT (Section 482(4) BNSS, 2023): Anticipatory bail under Section 482 BNSS "
                "does NOT apply to accusations under Section 65 or Section 70(2) of the Bharatiya Nyaya Sanhita, 2023, "
                "unless the Court holds that the basic ingredients of the offence are prima facie absent on the face of the FIR "
                "(cf. Prathvi Raj Chauhan v. Union of India, (2020) 4 SCC 727)."
            )
        else:
            alerts.append(
                "MANDATORY VICTIM HEARING NOTICE (Section 483(1)(a) Proviso & Section 483(2) BNSS, 2023): "
                "Presence of the informant or any person authorized by him is obligatory at the hearing of a Regular Bail "
                "application involving Section 65 or Section 70(2) of the BNS, 2023."
            )
    return alerts


def generate_bail_bundle(
    bail_type="482",
    forum="hc",
    petitioner="Sri [Name of Petitioner], S/o [Father's Name], Aged about 33 years, R/at Bengaluru",
    rank="Accused No. 1",
    ps="Cubbon Park Police Station, Bengaluru",
    crime_no="Crime No. ___/2026",
    offences="Sections 318(4), 316(2), and 61(2) of the Bharatiya Nyaya Sanhita, 2023",
    max_punishment="up_to_7",
    arrest_date_str=None,
    facts_text=None,
    source_file=None,
):
    os.makedirs(BAIL_OUT_DIR, exist_ok=True)
    today = datetime.date.today()
    today_str = today.strftime("%d.%m.%Y")

    # Auto-adjust forum if section 480 is chosen
    if bail_type == "480":
        forum = "magistrate"

    f_cfg = FORUM_CONFIG.get(forum, FORUM_CONFIG["hc"])
    respondent_block = f_cfg["respondent_desc"].format(ps=ps)
    case_no_line = f_cfg["case_prefix"].format(crime_no=crime_no)

    if source_file:
        extracted = extract_text_from_file(source_file)
        if extracted:
            facts_text = (
                f"Extracted from source record (`{os.path.basename(source_file)}`): "
                + re.sub(r"\s+", " ", extracted[:900])
                + "..."
            )

    if not facts_text:
        facts_text = (
            f"The Complainant lodged a First Information Report registered as {crime_no} before the Respondent "
            f"{ps} alleging offences punishable under {offences}. A plain reading of the complaint averments "
            f"demonstrates that the allegations are ex-facie civil/commercial or actuated by mala fides, and "
            f"do not disclose the essential ingredients of mens rea attributable to the Petitioner ({rank})."
        )

    # Custody calculation for Regular Bail (480 / 483)
    custody_days = 0
    arrest_formatted = "[Date of Arrest]"
    if arrest_date_str:
        try:
            a_dt = datetime.datetime.strptime(arrest_date_str, "%Y-%m-%d").date()
            custody_days = (today - a_dt).days + 1
            arrest_formatted = a_dt.strftime("%d.%m.%Y")
        except ValueError:
            pass

    statutory_alerts = check_statutory_bars_and_notices(bail_type, offences)

    # Provision titles & prayers based on bail_type (480 / 482 / 483)
    if bail_type == "482":
        section_heading = "MEMORANDUM OF CRIMINAL PETITION UNDER SECTION 482 OF THE BHARATIYA NAGARIK SURAKSHA SANHITA, 2023 (FOR ANTICIPATORY BAIL)"
        ia_section = "UNDER SECTION 482(1) READ WITH SECTION 528 OF THE BHARATIYA NAGARIK SURAKSHA SANHITA, 2023"
        custody_status_line = f"Apprehending arrest in {crime_no} registered by {ps}"
        main_prayer = (
            f"Wherefore, the Petitioner ({rank}) most respectfully prays that this {f_cfg['court_short']} may be pleased to:\n\n"
            f"1. **ALLOW** this Petition and direct the Respondent Police ({ps}) to forthwith release the Petitioner on bail in the event of his arrest in **{crime_no}** registered for the alleged offences punishable under **{offences}**, pending on the file of the jurisdictional Trial Court at Bengaluru, on such terms and conditions as this {f_cfg['court_short']} deems fit; and\n"
            f"2. Pass such other and further orders as this {f_cfg['court_short']} deems just and necessary in the interest of justice and personal liberty under Article 21 of the Constitution of India."
        )
        ia_prayer = (
            f"Grant **AD-INTERIM ANTICIPATORY BAIL** directing the Respondent ({ps}) not to take coercive steps or arrest the Petitioner ({rank}) in **{crime_no}**, or to release him forthwith in the event of arrest, pending disposal of the main Criminal Petition."
        )
    elif bail_type == "483":
        section_heading = "MEMORANDUM OF CRIMINAL PETITION UNDER SECTION 483 OF THE BHARATIYA NAGARIK SURAKSHA SANHITA, 2023 (FOR REGULAR BAIL)"
        ia_section = "UNDER SECTION 483(1) READ WITH SECTION 528 OF THE BHARATIYA NAGARIK SURAKSHA SANHITA, 2023"
        custody_status_line = f"In Judicial Custody at Central Prison, Parappana Agrahara, Bengaluru since {arrest_formatted} ({custody_days} days elapsed)"
        main_prayer = (
            f"Wherefore, the Petitioner ({rank}) most respectfully prays that this {f_cfg['court_short']} may be pleased to:\n\n"
            f"1. **ALLOW** this Petition and enlarge the Petitioner ({rank}) on **REGULAR BAIL** in **{crime_no}** registered by the Respondent ({ps}) for the offences punishable under **{offences}**, now pending on the file of the jurisdictional Court at Bengaluru; and\n"
            f"2. Pass such other and further orders as this {f_cfg['court_short']} deems fit in the interest of justice and equity."
        )
        ia_prayer = (
            f"Enlarge the Petitioner ({rank}) on **INTERIM REGULAR BAIL** in **{crime_no}** of {ps}, pending final disposal of the above Bail Petition, in the interest of justice."
        )
    else:  # 480
        section_heading = "APPLICATION UNDER SECTION 480 OF THE BHARATIYA NAGARIK SURAKSHA SANHITA, 2023 (FOR REGULAR BAIL BEFORE MAGISTRATE)"
        ia_section = "UNDER SECTION 480(1) OF THE BHARATIYA NAGARIK SURAKSHA SANHITA, 2023"
        custody_status_line = f"Produced / In Judicial Custody since {arrest_formatted} ({custody_days} days elapsed)"
        main_prayer = (
            f"Wherefore, the Applicant / {rank} most respectfully prays that this Hon'ble Court may be pleased to enlarge him on **REGULAR BAIL** under Section 480 of the Bharatiya Nagarik Suraksha Sanhita, 2023 in **{crime_no}** of {ps} for the alleged offences under **{offences}**, on such terms and sureties as this Hon'ble Court deems fit."
        )
        ia_prayer = (
            f"Grant **INTERIM BAIL** to the Applicant ({rank}) pending consideration of objections by the learned Assistant Public Prosecutor."
        )

    # Construct 10 Structured Grounds grounded in BNS/BNSS/BSA & Supreme Court Precedents
    grounds = []
    grounds.append(
        "**1. Innocence & Absence of Prima Facie Mens Rea:** The Petitioner is wholly innocent of the alleged offences and has been falsely implicated. Even if the allegations in the First Information Report are taken at face value, the essential statutory ingredients of the offences under "
        f"{offences} are conspicuously absent."
    )

    if max_punishment == "up_to_7":
        grounds.append(
            "**2. Mandatory Compliance with Section 35(3)–(6) BNSS, 2023 (Arnesh Kumar & Satender Kumar Antil Mandate):** "
            "The offences alleged carry a maximum punishment of seven (7) years or less. Under **Section 35(1)(b) and Section 35(3) of the Bharatiya Nagarik Suraksha Sanhita, 2023** (formerly Sections 41 and 41A CrPC), routine arrest is strictly barred, and issuance of a Notice of Appearance is mandatory. In *Arnesh Kumar v. State of Bihar*, (2014) 8 SCC 273 and *Satender Kumar Antil v. Central Bureau of Investigation*, (2022) 10 SCC 51, the Hon'ble Supreme Court held that non-compliance with pre-arrest notice requirements entitles the accused to immediate grant of bail."
        )
    else:
        grounds.append(
            "**2. Parameters of Prima Facie Case & Gravity (Sanjay Chandra Principle):** "
            "In *Sanjay Chandra v. Central Bureau of Investigation*, (2012) 1 SCC 40, the Hon'ble Supreme Court held that deprivation of liberty must be considered a punishment unless demonstrably required to ensure that the accused stands trial, and the object of bail is neither punitive nor preventative."
        )

    if bail_type in ("480", "483"):
        grounds.append(
            f"**3. Violation of Article 22(1) & Section 47 BNSS, 2023 (Written Grounds of Arrest):** "
            f"The Petitioner was taken into custody on {arrest_formatted} ({custody_days} days in custody). Under **Section 47 of the Bharatiya Nagarik Suraksha Sanhita, 2023** and Article 22(1) of the Constitution, the arresting officer is mandatorily required to communicate full **written grounds of arrest** (distinct from formal 'reasons for arrest') simultaneously upon arrest, as laid down by the Hon'ble Supreme Court in *Prabir Purkayastha v. State (NCT of Delhi)*, (2024) 8 SCC 254 and *Pankaj Bansal v. Union of India*, (2024) 7 SCC 576."
        )
        grounds.append(
            "**4. Custodial Interrogation Completed & Second Proviso to Section 480(1) BNSS:** "
            "All material recovery and preliminary statements under Section 180 BNSS have been recorded. Under the **Second Proviso to Section 480(1) of the BNSS, 2023**, bail cannot be refused merely on the ground that the accused may be required for witness identification (Section 54 BNSS) or further police custody beyond the initial 15-day period."
        )
    else:
        grounds.append(
            "**3. Constitution Bench Standard for Anticipatory Bail (Sushila Aggarwal & Gurbaksh Singh Sibbia):** "
            "In *Gurbaksh Singh Sibbia v. State of Punjab*, (1980) 2 SCC 565 and the 5-Judge Constitution Bench judgment in *Sushila Aggarwal v. State (NCT of Delhi)*, (2020) 5 SCC 1, the Hon'ble Supreme Court held that **Section 482 BNSS (formerly Section 438 CrPC)** is an essential safeguard of personal liberty under Article 21, and when an accused is ready to cooperate with the investigation, custodial interrogation is unwarranted unless specific recovery is impossible without arrest."
        )
        grounds.append(
            "**4. Willingness to Cooperate under Section 482(2) BNSS, 2023:** "
            "The Petitioner undertakes to appear before the Investigating Officer as and when required, make himself available for interrogation, and strictly abide by all conditions imposed under **Section 482(2)(i)–(iv) of the BNSS, 2023**."
        )

    grounds.append(
        "**5. Documentary & Electronic Nature of Evidence (Section 63 BSA, 2023):** "
        "The prosecution case rests primarily upon documentary and electronic records already in the possession of the Complainant/Investigating Agency. Consequently, there is zero possibility of the Petitioner tampering with evidence or influencing prosecution witnesses."
    )
    grounds.append(
        "**6. Bail is the Rule and Jail is the Exception (Gudikanti Narasimhulu & Manish Sisodia):** "
        "As reiterated by the Hon'ble Supreme Court in *Gudikanti Narasimhulu v. Public Prosecutor*, (1978) 1 SCC 240 and *Manish Sisodia v. Directorate of Enforcement*, 2024 INSC 595, prolonged pre-trial incarceration or unnecessary deprivation of liberty prior to conviction violates Article 21 of the Constitution."
    )
    grounds.append(
        "**7. Deep Roots in Society & Absence of Flight Risk (Triple Test Satisfied):** "
        "The Petitioner is a permanent resident of Bengaluru, Karnataka, having deep-rooted family and professional ties in the community. The Petitioner satisfies the **Triple Test** for grant of bail: (i) he is not a flight risk, (ii) he will not tamper with evidence, and (iii) he will not influence witnesses."
    )
    grounds.append(
        "**8. Readiness to Furnish Solvent Surety:** "
        "The Petitioner is ready and willing to furnish reliable, solvent local surety and execute a bail bond under **Section 484 / Section 485 of the BNSS, 2023** to the satisfaction of the Court."
    )

    #Affidavit deponent logic (Petitioner himself for 482; Relative/Parokar for 480/483 in custody)
    if bail_type == "482":
        affidavit_block = f"""## VERIFYING AFFIDAVIT

I, **{petitioner}**, do hereby solemnly affirm and state on oath as follows:

1. I am the Petitioner ({rank}) in the above Criminal Petition and I am thoroughly conversant with the facts of the case. Hence, I am swearing to this Affidavit.
2. I state that the averments made in Paragraphs 1 to 12 of the accompanying Memorandum of Criminal Petition under Section 482 of the Bharatiya Nagarik Suraksha Sanhita, 2023 and the Synopsis are true and correct to the best of my knowledge, information, and belief.
3. I further declare in compliance with the judgment of the Hon'ble Supreme Court in *Kusha Duruka v. State of Odisha*, (2024) 4 SCC 432 that no other bail petition concerning **{crime_no}** of **{ps}** is pending before this Hon'ble Court or any other Court.
4. The Annexures produced along with the Petition are true copies of their respective originals.

**VERIFICATION**
I, the Deponent above named, do hereby verify that the contents of this Affidavit are true and correct to the best of my knowledge, belief, and information.

**Identified by me:**

**ADVOCATE**                                                      **DEPONENT**
**BENGALURU**
**DATE: {today_str}**"""
    else:
        affidavit_block = f"""## VERIFYING AFFIDAVIT OF PAROKAR / RELATIVE
*(Filed on behalf of the Petitioner who is presently in Judicial Custody at Central Prison, Parappana Agrahara, Bengaluru)*

I, **[Name of Relative / Parokar]**, S/o / W/o [Name], aged about ____ years, residing at Bengaluru, Karnataka, do hereby solemnly affirm and state on oath as follows:

1. I am the [Brother / Wife / Father] of the Petitioner ({rank}) in the above Criminal Petition. Since the Petitioner is presently in Judicial Custody at Central Prison, Parappana Agrahara, Bengaluru in connection with **{crime_no}** of **{ps}**, I am swearing to this Affidavit on his behalf upon instructions and perusal of the case papers.
2. I state that the statements made in Paragraphs 1 to 12 of the accompanying Bail Petition under Section {bail_type} of the Bharatiya Nagarik Suraksha Sanhita, 2023 are true to the best of my information and belief.
3. I declare in compliance with *Kusha Duruka v. State of Odisha*, (2024) 4 SCC 432 that no other parallel bail application on behalf of the Petitioner is pending before any Court.

**Identified by me:**

**ADVOCATE**                                                      **DEPONENT (PAROKAR)**
**BENGALURU**
**DATE: {today_str}**"""

    md_bundle = f"""# {f_cfg['court_header']}
### {f_cfg['jurisdiction_title']}
## {case_no_line}
*(Under Section {bail_type} of the Bharatiya Nagarik Suraksha Sanhita, 2023)*
**(In {crime_no} of {ps})**

**BETWEEN:**

**{petitioner}**
*(Presently: {custody_status_line})*
... **PETITIONER ({rank.upper()})**

**AND:**

**{respondent_block}**
... **RESPONDENT / COMPLAINANT**

---

## I. SYNOPSIS & CHRONOLOGICAL LIST OF DATES

| Sl. No. | Date | Milestone / Event |
| :--- | :--- | :--- |
| 1. | **Prior to FIR** | Factual background between the parties; Petitioner is a law-abiding citizen residing at Bengaluru with zero flight risk. |
| 2. | **[Date of FIR]** | Registration of **{crime_no}** by Respondent **{ps}** invoking **{offences}**, arraigning the Petitioner as **{rank}**. |
| 3. | **{arrest_formatted if bail_type != '482' else today_str}** | {f"Petitioner arrested and remanded to Judicial Custody ({custody_days} days elapsed)." if bail_type != '482' else "Respondent Police attempting to apprehend the Petitioner without mandatory compliance under Section 35(3) BNSS, 2023."} |
| 4. | **{today_str}** | Hence, this Petition seeking grant of {'Anticipatory Bail under Section 482 BNSS' if bail_type == '482' else f'Regular Bail under Section {bail_type} BNSS'}. |

---

## II. {section_heading}

The Petitioner above named most respectfully submits as follows:

1. **PARTICULARS OF THE IMPUGNED PROCEEDINGS:**
   - **Police Station:** {ps}
   - **Crime / FIR Number:** {crime_no}
   - **Offences Alleged:** {offences}
   - **Rank of Petitioner:** {rank}
   - **Custody / Apprehension Status:** {custody_status_line}

2. **BRIEF FACTS OF THE CASE:**
   {facts_text}

3. **MANDATORY DISCLOSURE OF PRIOR BAIL APPLICATIONS & ANTECEDENTS (Per *Kusha Duruka v. State of Odisha*, (2024) 4 SCC 432):**
   - **(a) Prior / Parallel Bail Applications:** The Petitioner declares that `{ "no earlier bail application has been filed or is pending before any Court" if forum != "hc" else "after rejection of Crl. Misc. No. ____/2026 by the learned Sessions Judge / no other parallel petition is pending before this Hon'ble Court or the Hon'ble Supreme Court" }` in respect of {crime_no}.
   - **(b) Criminal Antecedents:** The Petitioner is a law-abiding citizen and has **no prior criminal convictions**. `[If any other FIR exists, disclose Crime No., Police Station, Offences, and Bail Status here]`.

---

## III. GROUNDS FOR BAIL

{chr(10).join(grounds)}

---

## IV. STATUTORY COMPLIANCE ALERTS (AUTOMATICALLY AUDITED BY SWEETYAI)
"""
    if statutory_alerts:
        for al in statutory_alerts:
            md_bundle += f"- **{al}**\n"
    else:
        md_bundle += (
            f"- **Section 482(4) / 483(2) BNSS Check:** `CLEAN` — Offences cited (`{offences}`) do not trigger the statutory bar under Section 65 or Section 70(2) of the BNS, 2023.\n"
        )

    md_bundle += f"""
---

## V. PRAYER

{main_prayer}

**BENGALURU**  
**DATE: {today_str}**  

**ADVOCATE FOR THE PETITIONER**

---

# {f_cfg['court_header']}
## I.A. No. 1 / 2026 IN {case_no_line}
**({ia_section})**

## APPLICATION FOR INTERIM BAIL

For the reasons stated in the accompanying Memorandum of Petition and Verifying Affidavit, the Petitioner ({rank}) most respectfully prays that this {f_cfg['court_short']} may be pleased to:

> {ia_prayer}

**BENGALURU**  
**DATE: {today_str}**  

**ADVOCATE FOR THE PETITIONER**

---

{affidavit_block}
"""

    slug_crime = re.sub(r"[^A-Za-z0-9]", "_", crime_no).strip("_").lower()
    out_path = os.path.join(BAIL_OUT_DIR, f"bail_sec{bail_type}_{forum}_{slug_crime}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md_bundle)

    print("\n=== SweetyAI Bail Petition & Affidavit Generator (BNSS 2023) ===")
    print(f"Bail Provision  : Section {bail_type} BNSS, 2023")
    print(f"Target Forum    : {f_cfg['court_header']}")
    print(f"Crime & Station : {crime_no} | {ps}")
    print(f"Offences Cited  : {offences}")
    print("=========================================================================")
    print(f"[Success] Complete Bail Filing Bundle saved -> '{out_path}'")
    print(f"          (Run `python3 sweety.py export {out_path}` for High Court A4 HTML)")
    print("=========================================================================\n")


def handle_bail_cli(argv):
    parser = argparse.ArgumentParser(
        prog="sweety legal bail",
        description="Generate Regular and Anticipatory Bail Petitions under Sections 480, 482, and 483 BNSS, 2023.",
    )
    parser.add_argument(
        "--type",
        default="482",
        help="480 (Magistrate Regular Bail), 482 (Anticipatory Bail), 483 (Sessions/HC Regular Bail); aliases 'regular', 'anticipatory', 'default' accepted",
    )
    parser.add_argument(
        "--forum",
        choices=["hc", "sessions", "magistrate"],
        default="hc",
        help="hc (High Court of Karnataka), sessions (Principal City Civil & Sessions Judge, Bengaluru), magistrate (ACJM/CJM)",
    )
    parser.add_argument("--petitioner", default="Sri [Name of Petitioner], Aged about 33 years, R/at Bengaluru", help="Petitioner name and details")
    parser.add_argument("--rank", default="Accused No. 1", help="Accused rank in FIR / Charge Sheet")
    parser.add_argument("--ps", default="Cubbon Park Police Station, Bengaluru", help="Police Station name")
    parser.add_argument("--crime-no", default="Crime No. 142/2026", help="FIR / Crime Number")
    parser.add_argument("--offences", default="Sections 318(4), 316(2), and 61(2) of BNS, 2023", help="Offences invoked in FIR")
    parser.add_argument("--max-punishment", choices=["up_to_7", "above_7"], default="up_to_7", help="Offence punishment tier (up_to_7 triggers Sec. 35(3) BNSS / Arnesh Kumar ground)")
    parser.add_argument("--arrest-date", default=None, help="Date of arrest YYYY-MM-DD (for Regular Bail under Sec. 480 / 483)")
    parser.add_argument("--facts", default=None, help="Custom factual summary string")
    parser.add_argument("--from-file", default=None, help="Extract FIR/complaint facts from a PDF, DOCX, MD, or TXT file")
    parser.add_argument("--latest", action="store_true", help="Automatically extract FIR/case facts from the newest file in ~/Downloads")
    args = parser.parse_args(argv)

    _type_aliases = {
        "regular": "480", "bail": "480", "sec480": "480", "480": "480",
        "anticipatory": "482", "482": "482", "pre-arrest": "482",
        "default": "483", "483": "483",
    }
    args.type = _type_aliases.get(str(args.type).strip().lower(), args.type)
    if args.type not in ("480", "482", "483"):
        parser.error(f"argument --type: invalid value '{args.type}' (choose from 480, 482, 483, or aliases regular/anticipatory/default)")

    source_file = get_latest_download() if args.latest else args.from_file

    generate_bail_bundle(
        bail_type=args.type,
        forum=args.forum,
        petitioner=args.petitioner,
        rank=args.rank,
        ps=args.ps,
        crime_no=args.crime_no,
        offences=args.offences,
        max_punishment=args.max_punishment,
        arrest_date_str=args.arrest_date,
        facts_text=args.facts,
        source_file=source_file,
    )


if __name__ == "__main__":
    handle_bail_cli(sys.argv[1:])
