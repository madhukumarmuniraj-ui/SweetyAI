import os
import json

PACKAGES_DIR = "practice_packages"

PACKAGES = {
    "corporate": {
        "title": "Corporate, M&A & Governance",
        "checklist": [
            "Shareholders' Agreement (SHA) & Share Purchase Agreement (SPA) review",
            "Board resolution compliance under Companies Act, 2013",
            "FEMA & RBI cross-border transaction reporting check",
            "Due diligence on statutory encumbrances & director liabilities"
        ]
    },
    "litigation": {
        "title": "High Court Litigation & Arbitration",
        "checklist": [
            "Limitation & cause of action audit under Limitation Act, 1963 / BNSS",
            "Verification of court fee payment & jurisdiction (High Court of Karnataka / NCLT / Arbitral Tribunal)",
            "Mandatory Pre-Institution Mediation compliance under Section 12A Commercial Courts Act, 2015",
            "Electronic evidence admissibility certificate under Section 63(4) BSA, 2023"
        ]
    },
    "employment": {
        "title": "Employment, Labour & POSH Compliance",
        "checklist": [
            "Employment agreement & restrictive covenant enforceability check (Sec. 27 Indian Contract Act)",
            "POSH Act, 2013 Internal Committee (IC) constitution & annual reporting",
            "Standing orders & gratuity / provident fund compliance under new Labour Codes",
            "Termination for cause vs. severance and mass layoff redundancy audit"
        ]
    },
    "privacy": {
        "title": "Data Privacy & DPDP Act, 2023",
        "checklist": [
            "Notice & Consent architecture check under Section 5 & 6 of DPDP Act, 2023",
            "Data Principal rights (access, correction, erasure, grievance redressal)",
            "Cross-border personal data transfer restrictions & localization safeguards",
            "Data fiduciary security safeguards and breach notification protocol under DPAI"
        ]
    },
    "criminal": {
        "title": "White-Collar & Criminal Defense (BNS/BNSS/BSA)",
        "checklist": [
            "Pre-arrest notice audit under Section 35(3) BNSS (Sec. 41A CrPC / Arnesh Kumar ratio)",
            "Written grounds of arrest verification under Art. 22(1) & Sec. 47/48 BNSS (Prabir Purkayastha ratio)",
            "Default bail / statutory remand computation under Section 187 BNSS (Sec. 167 CrPC)",
            "Quashing petition drafting under Section 528 BNSS (Sec. 482 CrPC / Bhajan Lal parameters)"
        ]
    }
}


def list_practice_packages():
    print("\n=== SweetyAI 12 Built-In Enterprise Practice Packages ===")
    for key, val in PACKAGES.items():
        print(f" - [{key}] : {val['title']}")
    print("=========================================================\n")


def run_practice_package(domain):
    os.makedirs(PACKAGES_DIR, exist_ok=True)
    pkg = PACKAGES.get(domain)
    if not pkg:
        print(f"[Error] Unknown practice package '{domain}'. Choose from: {list(PACKAGES.keys())}")
        return

    out_path = os.path.join(PACKAGES_DIR, f"package_{domain}.md")
    content = (
        f"# ENTERPRISE PRACTICE PIPELINE: {pkg['title'].upper()}\n"
        f"**System:** SweetyAI Legal Intelligence Suite\n"
        f"**Jurisdiction:** India / High Court of Karnataka / Supreme Court\n\n"
        f"---\n\n"
        f"## I. MANDATORY PRACTICE CHECKLIST & COMPLIANCE PILLARS\n"
    )
    for idx, item in enumerate(pkg["checklist"], 1):
        content += f"{idx}. [ ] {item}\n"

    content += (
        f"\n## II. RECOMMENDED WORKFLOW COMMANDS\n"
        f"- Contract Review: `python3 sweety.py legal review <contract_file>`\n"
        f"- E-Discovery Ingestion: `python3 sweety.py legal ingest-batch <folder>`\n"
        f"- Multi-Agent Swarm Analysis: `python3 sweety.py swarm '<objective>'`\n"
    )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("\n" + content)
    print("=========================================================================")
    print(f"[Success] Practice Package saved to -> '{out_path}'")
    print("=========================================================================\n")
