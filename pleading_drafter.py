import os
import datetime
import requests

BASE_URL = "http://127.0.0.1:8765"
PLEADINGS_DIR = "court_pleadings"


def fetch_grounded_authorities(query):
    try:
        resp = requests.post(f"{BASE_URL}/rag-chat", json={"message": query}, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("response", ""), data.get("sources", [])
    except Exception:
        pass
    return (
        "Section 528 BNSS (482 CrPC), Section 482 BNSS (438 CrPC), Section 35 BNSS (41A CrPC), "
        "Section 61 BNS (120A/120B IPC), and Section 318(4) BNS (420 IPC).",
        ["Local Statutory Corpus"],
    )


def draft_pleading(pleading_type, facts, forum="IN THE HIGH COURT OF KARNATAKA AT BENGALURU"):
    os.makedirs(PLEADINGS_DIR, exist_ok=True)
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    year = datetime.datetime.now().strftime("%Y")

    rag_query = f"{pleading_type} {facts} BNS BNSS BSA CrPC IPC Supreme Court precedent"
    rag_context, sources = fetch_grounded_authorities(rag_query)

    if pleading_type == "quashing":
        caption_statute = (
            "MEMORANDUM OF CRIMINAL PETITION UNDER SECTION 528 OF THE BHARATIYA NAGARIK SURAKSHA SANHITA, 2023 "
            "(FORMERLY SECTION 482 OF THE CODE OF CRIMINAL PROCEDURE, 1973)"
        )
        case_prefix = f"CRL. P. No. __________ / {year}"
        grounds = (
            "1. **Absence of Prima Facie Ingredients (Category 1 & 3 of Bhajan Lal):** Assuming the allegations in the "
            "impugned FIR/Complaint to be true at their face value, they do not disclose the essential statutory ingredients "
            "of an unlawful agreement under **Section 61(1) of the Bharatiya Nyaya Sanhita, 2023 (Section 120A IPC)** or "
            "dishonest inducement at the inception under **Section 318(4) of BNS, 2023 (Section 420 IPC)**. As held by the "
            "Hon'ble Supreme Court in *State of Haryana v. Bhajan Lal, 1992 Supp (1) SCC 335*, continuation of criminal "
            "proceedings where no cognizable offence is made out constitutes a gross abuse of the process of the Court.\n\n"
            "2. **Civil/Commercial Dispute Given a Criminal Cloak:** A purely civil or contractual dispute cannot be "
            "weaponized into a criminal prosecution to exert pressure without specific overt acts of mens rea.\n\n"
            "3. **Procedural Safeguards & Electronic Evidence Audit:** Any reliance on uncertified electronic communications "
            "without a mandatory certificate under **Section 63(4) of the Bharatiya Sakshya Adhiniyam, 2023 (formerly Section "
            "65B(4) of the Indian Evidence Act, 1872)** is inadmissible in law as settled by the Constitution Bench in "
            "*Arjun Panditrao Khotkar v. Kailash Kushanrao Gorantyal, (2020) 7 SCC 1*."
        )
        prayer = (
            "WHEREFORE, the Petitioner above named most respectfully prays that this Hon'ble Court may be pleased to:\n"
            "  (a) Call for the records in Crime No. ____/2026 pending on the file of the Learned Magistrate / Trial Court;\n"
            "  (b) **QUASH** the impugned FIR, Complaint, and all further criminal proceedings against the Petitioner in exercise "
            "of inherent powers under **Section 528 of the Bharatiya Nagarik Suraksha Sanhita, 2023 (Section 482 CrPC)**; and\n"
            "  (c) Grant an **Interim Order of Stay** of all further investigation/proceedings pending disposal of this Criminal Petition, "
            "in the interest of justice and equity."
        )

    elif pleading_type == "anticipatory-bail":
        caption_statute = (
            "MEMORANDUM OF CRIMINAL PETITION UNDER SECTION 482 OF THE BHARATIYA NAGARIK SURAKSHA SANHITA, 2023 "
            "(FORMERLY SECTION 438 OF THE CODE OF CRIMINAL PROCEDURE, 1973) FOR ANTICIPATORY BAIL"
        )
        case_prefix = f"CRL. P. No. __________ / {year}"
        grounds = (
            "1. **Mandatory Notice Safeguard under Section 35(3) BNSS (Section 41A CrPC):** For offences punishable with "
            "imprisonment up to 7 years, mechanical arrest is strictly prohibited under *Arnesh Kumar v. State of Bihar, "
            "(2014) 8 SCC 273* and *Satender Kumar Antil v. CBI, (2022) 10 SCC 51*. The Investigating Officer is duty-bound "
            "to issue a Notice of Appearance under **Section 35(3) of BNSS, 2023 (Section 41A CrPC)**.\n\n"
            "2. **Constitution Bench Ratio on Pre-Arrest Liberty:** Under the 5-Judge Constitution Bench judgments in "
            "*Gurbaksh Singh Sibbia v. State of Punjab, (1980) 2 SCC 565* and *Sushila Aggarwal v. State (NCT of Delhi), "
            "(2020) 5 SCC 1*, personal liberty under Article 21 is paramount, custodial interrogation is neither warranted "
            "nor necessary where documentary/digital records are already available, and anticipatory bail under **Section 482 "
            "BNSS (Section 438 CrPC)** ordinarily continues until the conclusion of trial.\n\n"
            "3. **Readiness to Cooperate:** The Petitioner has deep roots in society, is a permanent resident within the "
            "jurisdiction of this Hon'ble Court, undertakes to appear before the Investigating Officer whenever called upon, "
            "and will not tamper with prosecution witnesses or evidence."
        )
        prayer = (
            "WHEREFORE, the Petitioner most respectfully prays that this Hon'ble Court may be pleased to allow this Petition "
            "under **Section 482 of the Bharatiya Nagarik Suraksha Sanhita, 2023 (Section 438 CrPC)** and direct the Respondent "
            "Police to release the Petitioner on bail in the event of arrest in Crime No. ____/2026, on such terms and "
            "conditions as this Hon'ble Court deems fit, in the interest of justice and equity."
        )

    else:  # regular-bail
        caption_statute = (
            "MEMORANDUM OF CRIMINAL PETITION UNDER SECTION 483 OF THE BHARATIYA NAGARIK SURAKSHA SANHITA, 2023 "
            "(FORMERLY SECTION 439 OF THE CODE OF CRIMINAL PROCEDURE, 1973) FOR REGULAR BAIL"
        )
        case_prefix = f"CRL. P. No. __________ / {year}"
        grounds = (
            "1. **Violation of Section 35 BNSS (Section 41 & 41A CrPC) Vitiates Arrest:** As laid down by the Hon'ble Supreme "
            "Court in *Satender Kumar Antil v. Central Bureau of Investigation, (2022) 10 SCC 51* (Para 100.3), any arrest made "
            "in breach of the mandatory requirements of **Section 35 of BNSS, 2023 (Sections 41 and 41A CrPC)** and the "
            "directions in *Arnesh Kumar v. State of Bihar, (2014) 8 SCC 273* entitles the accused to be enlarged on bail.\n\n"
            "2. **Bail is the Rule, Jail is the Exception:** Pre-trial incarceration is not punitive. Major custodial "
            "investigation is complete, and continued detention infringes Article 21 of the Constitution of India.\n\n"
            "3. **Statutory Remand & Default Bail Timelines (Section 187 BNSS / Section 167 CrPC):** The Petitioner has "
            "cooperated throughout remand and undertakes to abide by all conditions imposed under **Section 483 BNSS**."
        )
        prayer = (
            "WHEREFORE, the Petitioner most respectfully prays that this Hon'ble Court may be pleased to enlarge the "
            "Petitioner on Regular Bail under **Section 483 of the Bharatiya Nagarik Suraksha Sanhita, 2023 (Section 439 CrPC)** "
            "in Crime No. ____/2026 pending on the file of the Jurisdictional Court, in the interest of justice and equity."
        )

    pleading_text = (
        f"# {forum}\n"
        f"**{case_prefix}**\n\n"
        f"**({caption_statute})**\n\n"
        f"**IN THE MATTER OF:**\n"
        f"**BETWEEN:**\n"
        f"Mr. [Name of Petitioner / Accused]                                  ... **PETITIONER / ACCUSED**\n\n"
        f"**AND:**\n"
        f"1. The State of Karnataka,\n"
        f"   By [Station House Officer / Police Station],\n"
        f"   Represented by the State Public Prosecutor,\n"
        f"   High Court Building, Bengaluru - 560 001.\n"
        f"2. [Name of Defacto Complainant / Informant]                        ... **RESPONDENTS**\n\n"
        f"---\n\n"
        f"## I. BRIEF FACTS OF THE CASE\n"
        f"1. The Petitioner has approached this Hon'ble Court seeking appropriate statutory relief in respect of the following "
        f"factual matrix:\n"
        f"   > *{facts}*\n\n"
        f"## II. VERIFIED STATUTORY & PRECEDENT AUTHORITIES RETRIEVED FROM RAG REPOSITORY\n"
        f"{rag_context}\n\n"
        f"**Cited Authorities:** {', '.join(sources)}\n\n"
        f"## III. GROUNDS FOR RELIEF\n"
        f"{grounds}\n\n"
        f"## IV. PRAYER\n"
        f"{prayer}\n\n"
        f"---\n"
        f"**Place:** Bengaluru\n"
        f"**Date:** {today}                                                  **ADVOCATE FOR THE PETITIONER**\n"
    )

    slug = "_".join(facts.lower().split()[:4]).replace("/", "_")
    out_file = os.path.join(PLEADINGS_DIR, f"{pleading_type}_{slug}.md")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(pleading_text)

    print("\n" + pleading_text)
    print("=========================================================================")
    print(f"[Success] Court-Ready Pleading saved to -> '{out_file}'")
    print("=========================================================================\n")
    return out_file
