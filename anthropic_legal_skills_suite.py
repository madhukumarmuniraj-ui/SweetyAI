import os
import sys
import re
import zipfile
import datetime
import argparse
import xml.etree.ElementTree as ET

NDA_OUT_DIR = "nda_triage_reports"
RISK_OUT_DIR = "risk_assessment_reports"
SKILL_SYNC_DIR = os.path.join("anthropic_plugins", "legal", "skills")
DOWNLOADS_DIR = os.path.expanduser("~/Downloads")
DOC_EXTENSIONS = (".pdf", ".docx", ".md", ".txt", ".doc", ".rtf")


def extract_doc_text(file_path):
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
    return text


def get_latest_download():
    if not os.path.exists(DOWNLOADS_DIR):
        return None
    files = [
        os.path.join(DOWNLOADS_DIR, f)
        for f in os.listdir(DOWNLOADS_DIR)
        if os.path.isfile(os.path.join(DOWNLOADS_DIR, f)) and not f.startswith(".")
    ]
    if not files:
        return None
    doc_files = [f for f in files if os.path.splitext(f)[1].lower() in DOC_EXTENSIONS]
    target = doc_files if doc_files else files
    target.sort(key=os.path.getmtime, reverse=True)
    return target[0]


def sync_all_anthropic_legal_skills():
    os.makedirs(SKILL_SYNC_DIR, exist_ok=True)
    skills_catalog = {
        "triage-nda.md": (
            "---\nname: triage-nda-india\n"
            "description: Rapid GREEN/YELLOW/RED triage of NDAs under Indian Contract Act 1872, Specific Relief Act 1963, and Karnataka Stamp Act 1957.\n---\n"
            "# NDA Triage Playbook (Indian Law Localized)\n"
            "1. Structure: Mutual vs Unilateral.\n"
            "2. Standard Carveouts: Public domain, prior possession, independent development, Court/Statutory compulsion.\n"
            "3. Survival Term: 2-5 years standard; perpetual survival restricted strictly to statutory Trade Secrets.\n"
            "4. Section 27 ICA Check: Flag any disguised post-termination non-compete or restraint of trade as RED.\n"
            "5. Remedies: Injunctive relief under Sec. 37-38 Specific Relief Act, 1963 & Order XXXIX Rules 1-2 CPC; reject punitive liquidated damages (Sec. 74 ICA).\n"
            "6. Stamp Duty: INR 500 under Article 5(j) of the Karnataka Stamp Act, 1957 (Act 04 of 2024).\n"
        ),
        "legal-risk-assessment.md": (
            "---\nname: legal-risk-assessment-india\n"
            "description: Severity x Likelihood (1-25) Legal Risk Matrix with Indian statutory escalation triggers.\n---\n"
            "# Legal Risk Assessment Matrix (GREEN / YELLOW / ORANGE / RED)\n"
            "- GREEN (Score 1-4): Standard commercial controls; approve at counsel level.\n"
            "- YELLOW (Score 5-9): Negotiate fallback redlines; log in Risk Register.\n"
            "- ORANGE (Score 10-15): Escalate to Senior Partner / General Counsel; prepare mitigation memo.\n"
            "- RED (Score 16-25): Critical statutory exposure (Uncapped liability, Sec. 12(5) A&C Act invalidity, DPDP Act Sec. 8(5) breach, or criminal cognizable trigger under BNS 2023). Immediate litigation hold.\n"
        ),
        "compliance-check-dpdp.md": (
            "---\nname: compliance-check-dpdp-india\n"
            "description: Indian Privacy & Regulatory Compliance Check under DPDP Act 2023, CERT-In 2022 Directions, and Sec. 132 BSA 2023.\n---\n"
            "# DPDP Act 2023 & Indian Regulatory Compliance Skill\n"
            "1. Notice & Consent (Secs. 5-6 DPDP Act, 2023): Verifiable notice in English + 8th Schedule languages.\n"
            "2. Data Fiduciary Safeguards (Sec. 8(5) DPDP Act): Mandatory security safeguards even when processing under Sec. 17(1)(a) legal claims exemption.\n"
            "3. CERT-In Incident Reporting: 6-hour mandatory reporting window for specified cybersecurity incidents.\n"
        ),
        "incident-and-daily-brief.md": (
            "---\nname: legal-briefing-india\n"
            "description: Daily, Topic, and Incident Legal Briefings with Litigation Hold & BSA Sec. 63(4) preservation alerts.\n---\n"
            "# Legal Briefing Skill (Daily / Topic / Incident)\n"
            "- Automatically flags Section 63(4) BSA electronic evidence preservation and Section 132 BSA privilege markers.\n"
        ),
    }
    for fname, content in skills_catalog.items():
        with open(os.path.join(SKILL_SYNC_DIR, fname), "w", encoding="utf-8") as f:
            f.write(content)
    print(f"[Synced] 4 Anthropic Legal Skills (Localized for Indian Law) installed in '{SKILL_SYNC_DIR}/'")


def run_nda_triage(file_path):
    os.makedirs(NDA_OUT_DIR, exist_ok=True)
    sync_all_anthropic_legal_skills()

    if not os.path.exists(file_path):
        print(f"[Error] File '{file_path}' not found.")
        return

    text = extract_doc_text(file_path)
    lower = text.lower()
    base_name = os.path.basename(file_path)
    today_str = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")

    criteria = []
    red_count = 0
    yellow_count = 0

    # 1. Mutual vs Unilateral Check
    is_mutual = any(k in lower for k in ["mutual", "each party", "either party", "disclosing party and receiving party"])
    if is_mutual:
        criteria.append(("1. Agreement Structure", "GREEN", "Mutual obligations detected across parties."))
    else:
        yellow_count += 1
        criteria.append(("1. Agreement Structure", "YELLOW", "Appears Unilateral; verify whether client is Disclosing or Receiving Party."))

    # 2. Standard 5 Carveouts (Public domain, prior knowledge, independent dev, third-party, court order)
    carveouts_found = sum(
        1 for k in ["publicly available", "public domain", "independently developed", "prior to disclosure", "court order", "required by law"]
        if k in lower
    )
    if carveouts_found >= 2:
        criteria.append(("2. Standard Confidentiality Carveouts", "GREEN", "Standard exclusions (public domain / independent development / legal compulsion) detected."))
    else:
        red_count += 1
        criteria.append(("2. Standard Confidentiality Carveouts", "RED", "Missing mandatory exclusions (Public knowledge, Prior possession, Independent development, and Court/Statutory compulsion)."))

    # 3. Term & Survival Duration (Perpetual vs 2-5 Years)
    has_perpetual = any(k in lower for k in ["perpetual", "in perpetuity", "indefinitely", "forever"])
    if has_perpetual:
        yellow_count += 1
        criteria.append(("3. Term & Survival Period", "YELLOW", "Perpetual confidentiality detected; restrict survival to 3 years (with trade secrets carved out)."))
    else:
        criteria.append(("3. Term & Survival Period", "GREEN", "No oppressive perpetual confidentiality lock-in detected."))

    # 4. Disguised Non-Compete / Restraint of Trade (Section 27 ICA, 1872)
    has_non_compete = any(k in lower for k in ["non-compete", "non compete", "not engage in any competing", "shall not compete"])
    if has_non_compete:
        red_count += 1
        criteria.append(("4. Section 27 ICA Restraint of Trade Check", "RED", "CRITICAL: Disguised Non-Compete clause inside NDA! Post-termination restraint of trade is VOID under Section 27 of the Indian Contract Act, 1872 (Percept D'Mark v. Zaheer Khan)."))
    else:
        criteria.append(("4. Section 27 ICA Restraint of Trade Check", "GREEN", "Clean — No disguised post-termination non-compete detected."))

    # 5. Remedies & Punitive Liquidated Damages (Section 74 ICA & Specific Relief Act)
    has_penalty = any(k in lower for k in ["liquidated damages of", "penalty of", "unlimited liability", "indemnify for all indirect"])
    if has_penalty:
        red_count += 1
        criteria.append(("5. Remedies & Damages (Sec. 73/74 ICA)", "RED", "CRITICAL: Punitive liquidated damages / uncapped liability detected in NDA. Restrict remedies to equitable injunctive relief under Sec. 37-38 Specific Relief Act, 1963 and direct provable damages under Sec. 73 ICA."))
    else:
        criteria.append(("5. Remedies & Damages (Sec. 73/74 ICA)", "GREEN", "Remedies aligned with standard injunctive and direct-damage principles."))

    # 6. Return/Destruction & Archival Retention Exception
    has_return = any(k in lower for k in ["return or destroy", "destruction", "archival", "backup"])
    if has_return:
        criteria.append(("6. Return / Destruction & Compliance Archival", "GREEN", "Return/destruction clause detected."))
    else:
        yellow_count += 1
        criteria.append(("6. Return / Destruction & Compliance Archival", "YELLOW", "Add return/destruction clause with a carve-out permitting retention of 1 archival copy for statutory/regulatory compliance and automated IT backups."))

    # 7. Governing Law, Arbitration & Karnataka Stamp Duty
    unilateral_arb = any(k in lower for k in ["solely appointed by", "appointed by the company", "unilateral"])
    if unilateral_arb:
        red_count += 1
        criteria.append(("7. Dispute Resolution & Stamp Duty", "RED", "Unilateral arbitrator appointment detected — VOID under Sec. 12(5) A&C Act, 1996 (CORE v. ECI SPIC, 2024 SC). Also ensure INR 500 e-Stamp under Art. 5(j) Karnataka Stamp Act, 1957."))
    else:
        criteria.append(("7. Dispute Resolution & Stamp Duty", "GREEN", "No unilateral arbitrator clause detected. Ensure INR 500 stamp duty under Article 5(j) of the Karnataka Stamp Act, 1957 (Act 04 of 2024)."))

    if red_count > 0:
        overall = "RED — ESCALATE FOR FULL COUNSEL REDLINE (DO NOT SIGN AS-IS)"
    elif yellow_count > 0:
        overall = "YELLOW — APPROVE WITH MINOR FALLBACK REDLINES"
    else:
        overall = "GREEN — STANDARD APPROVAL (ROUTE FOR SIGNATURE & INR 500 e-STAMP)"

    report = f"""# SWEETYAI NDA TRIAGE & PRE-SCREENING REPORT
*(Powered by Anthropic `knowledge-work-plugins/legal/triage-nda` — Localized for Indian Law)*

**Target Document:** `{file_path}`  
**Audit Timestamp:** {today_str}  
**OVERALL TRIAGE CLASSIFICATION:** **`{overall}`**  
**Flag Summary:** `{red_count} RED (Critical)` | `{yellow_count} YELLOW (Moderate)` | `{7 - red_count - yellow_count} GREEN (Compliant)`

---

## I. 7-POINT NDA SCREENING MATRIX

| Screening Criterion | Triage Flag | Legal Finding & Indian Statutory Rule |
| :--- | :--- | :--- |
"""
    for crit, flag, note in criteria:
        report += f"| **{crit}** | **`{flag}`** | {note} |\n"

    report += """
---

## II. MANDATORY FALLBACK CLAUSES FOR RED / YELLOW ITEMS
1. **Standard Carveouts & Legal Compulsion Proviso:**
   > *"Confidential Information shall not include information that: (a) is or becomes publicly available without breach; (b) was lawfully in Receiving Party's prior possession; (c) is independently developed without reference to Confidential Information; or (d) is required to be disclosed pursuant to an order of a Court of competent jurisdiction or statutory authority, provided prompt prior written notice is given where legally permissible."*
2. **Archival & Statutory Retention Carveout:**
   > *"Notwithstanding the obligation to return or destroy Confidential Information upon termination, the Receiving Party and its legal counsel may retain one (1) archival copy strictly for evidentiary, regulatory, or litigation defense purposes, and shall not be required to purge routine encrypted IT disaster-recovery backups."*
"""

    slug = re.sub(r"[^A-Za-z0-9_\-]", "_", os.path.splitext(base_name)[0])
    out_path = os.path.join(NDA_OUT_DIR, f"nda_triage_{slug}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)

    print("\n" + report)
    print("=========================================================================")
    print(f"[Success] NDA Triage Report saved -> '{out_path}'")
    print("=========================================================================\n")


def run_risk_register(file_path):
    os.makedirs(RISK_OUT_DIR, exist_ok=True)
    sync_all_anthropic_legal_skills()

    if not os.path.exists(file_path):
        print(f"[Error] File '{file_path}' not found.")
        return

    text = extract_doc_text(file_path)
    lower = text.lower()
    base_name = os.path.basename(file_path)
    today_str = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")

    # Severity (1-5) x Likelihood (1-5) Matrix from anthropics/knowledge-work-plugins/legal/skills/legal-risk-assessment
    risks = []

    if "unlimited liability" in lower or "limitation of liability" not in lower:
        risks.append(("Uncapped / Unstated Financial Liability (Sec. 73/74 ICA)", 5, 4, 20, "RED (CRITICAL)", "Insert 12-month fee cap and exclude indirect/consequential damages."))
    else:
        risks.append(("Contractual Liability Exposure (Sec. 73 ICA)", 2, 2, 4, "GREEN (LOW)", "Standard liability cap present; maintain contract monitoring."))

    if "solely appointed by" in lower or "appointed by the company" in lower:
        risks.append(("Void Unilateral Arbitrator Appointment (Sec. 12(5) A&C Act / CORE 2024 SC)", 5, 5, 25, "RED (CRITICAL)", "Replace with mutual appointment or Bengaluru Arbitration Centre rules."))
    else:
        risks.append(("Dispute Resolution & Arbitral Validity", 2, 1, 2, "GREEN (LOW)", "Clause complies with Section 12(5) A&C Act neutrality."))

    if "non-compete" in lower or "competing business" in lower:
        risks.append(("Void Post-Termination Non-Compete (Sec. 27 ICA, 1872)", 4, 4, 16, "RED (HIGH)", "Reframe as Non-Solicitation & Trade Secret protection clause."))

    if any(k in lower for k in ["fir", "318(4)", "420", "arrest", "cognizable", "138"]):
        risks.append(("Active Criminal / Quasi-Criminal Litigation Exposure (BNS / BNSS / NI Act)", 5, 4, 20, "RED (CRITICAL)", "Issue immediate Litigation Hold, preserve Sec. 63(4) BSA electronic records, and prepare Sec. 528 / 482 BNSS petition."))

    if re.search(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b", text) or "personal data" in lower:
        risks.append(("Personal Data & DPDP Act Section 8(5) Security Safeguard Duty", 3, 3, 9, "YELLOW (MEDIUM)", "Apply PII redaction (--scrub) prior to external sharing; maintain Sec. 8(5) DPDP Act encryption/access controls."))

    max_score = max((r[3] for r in risks), default=4)
    overall_band = "RED (CRITICAL — SENIOR COUNSEL ESCALATION & LITIGATION HOLD)" if max_score >= 16 else ("YELLOW (MEDIUM — MITIGATE & MONITOR)" if max_score >= 6 else "GREEN (LOW — STANDARD CONTROLS)")

    report = f"""# SWEETYAI LEGAL RISK REGISTER & ESCALATION MATRIX
*(Powered by Anthropic `legal-risk-assessment` Skill — Severity [1–5] × Likelihood [1–5] Framework)*

**Target Matter / File:** `{file_path}`  
**Assessment Timestamp:** {today_str}  
**Highest Risk Score:** `{max_score} / 25` — **`{overall_band}`**

---

## I. QUANTITATIVE RISK ASSESSMENT REGISTER

| # | Identified Legal Risk Factor | Severity (1-5) | Likelihood (1-5) | Risk Score (S×L) | Classification | Mandatory Mitigation / Escalation Action |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for idx, (r_name, sev, lik, score, band, action) in enumerate(risks, 1):
        report += f"| {idx}. | **{r_name}** | {sev} | {lik} | **{score}** | **`{band}`** | {action} |\n"

    slug = re.sub(r"[^A-Za-z0-9_\-]", "_", os.path.splitext(base_name)[0])
    out_path = os.path.join(RISK_OUT_DIR, f"risk_register_{slug}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)

    print("\n" + report)
    print("=========================================================================")
    print(f"[Success] Legal Risk Assessment Register saved -> '{out_path}'")
    print("=========================================================================\n")


def handle_anthropic_skills_cli(cmd, argv):
    if cmd == "triage-nda":
        parser = argparse.ArgumentParser(prog="sweety legal triage-nda", description="Rapid GREEN/YELLOW/RED NDA Triage under Indian Contract Act & Specific Relief Act.")
        parser.add_argument("file", nargs="?", help="Path to NDA file")
        parser.add_argument("--latest", action="store_true", help="Triage the newest file in ~/Downloads")
        args = parser.parse_args(argv)
        target = get_latest_download() if args.latest else args.file
        if not target:
            parser.print_help()
            return
        run_nda_triage(target)

    elif cmd == "risk-register":
        parser = argparse.ArgumentParser(prog="sweety legal risk-register", description="Generate a Severity x Likelihood (1-25) Legal Risk Assessment Register.")
        parser.add_argument("file", nargs="?", help="Path to contract, pleading, or case file")
        parser.add_argument("--latest", action="store_true", help="Assess risk on the newest file in ~/Downloads")
        args = parser.parse_args(argv)
        target = get_latest_download() if args.latest else args.file
        if not target:
            parser.print_help()
            return
        run_risk_register(target)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        handle_anthropic_skills_cli(sys.argv[1], sys.argv[2:])
    else:
        sync_all_anthropic_legal_skills()
