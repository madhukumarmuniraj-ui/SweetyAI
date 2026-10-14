import os
import sys
import re
import zipfile
import datetime
import argparse
import requests
import xml.etree.ElementTree as ET

BASE_URL = "http://127.0.0.1:8765"
REVIEW_OUT_DIR = "contract_review_reports"
DOWNLOADS_DIR = os.path.expanduser("~/Downloads")
DOC_EXTENSIONS = (".pdf", ".docx", ".txt", ".md", ".doc", ".rtf")


def extract_contract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    text_content = ""
    parser_used = "Plain-Text UTF-8 Reader"

    if ext == ".docx" and zipfile.is_zipfile(file_path):
        try:
            with zipfile.ZipFile(file_path, "r") as z:
                if "word/document.xml" in z.namelist():
                    doc_xml = ET.fromstring(z.read("word/document.xml"))
                    paragraphs = []
                    for p in doc_xml.iter():
                        if p.tag.endswith("}p"):
                            texts = [t.text for t in p.iter() if t.tag.endswith("}t") and t.text]
                            if texts:
                                paragraphs.append("".join(texts))
                    text_content = "\n".join(paragraphs)
                    parser_used = "Native DOCX XML Parser (word/document.xml)"
        except Exception as e:
            parser_used = f"DOCX Fallback ({e})"

    elif ext == ".pdf":
        try:
            try:
                import pymupdf as fitz
            except ImportError:
                import fitz
            doc = fitz.open(file_path)
            pages = [page.get_text() for page in doc]
            text_content = "\n".join(pages)
            parser_used = f"PyMuPDF Engine ({len(pages)} pages extracted)"
            doc.close()
        except Exception as e:
            parser_used = f"PDF Fallback Reader ({e})"

    if not text_content.strip():
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            text_content = f.read()

    return text_content, parser_used


def list_recent_download_contracts(limit=10):
    if not os.path.exists(DOWNLOADS_DIR):
        return []
    files = [
        os.path.join(DOWNLOADS_DIR, f)
        for f in os.listdir(DOWNLOADS_DIR)
        if os.path.isfile(os.path.join(DOWNLOADS_DIR, f)) and not f.startswith(".")
    ]
    # Prioritize document extensions, sorted by modification time
    doc_files = [f for f in files if os.path.splitext(f)[1].lower() in DOC_EXTENSIONS]
    target_list = doc_files if doc_files else files
    target_list.sort(key=os.path.getmtime, reverse=True)
    return target_list[:limit]


def evaluate_indian_statutory_playbook(text):
    lower = text.lower()
    findings = []

    # 1. Limitation of Liability & Liquidated Damages (Secs. 73 & 74 ICA, 1872)
    has_lol = any(k in lower for k in ["limitation of liability", "aggregate liability", "liability shall not exceed", "liability cap"])
    has_unlimited = any(k in lower for k in ["unlimited liability", "without limit", "penalty of", "punitive damages"])
    has_consequential_waiver = any(k in lower for k in ["indirect", "consequential", "special, or punitive", "loss of profit"])

    if not has_lol or has_unlimited:
        findings.append({
            "pillar": "1. Limitation of Liability & Damages (Secs. 73 & 74, Indian Contract Act, 1872)",
            "severity": "CRITICAL DEVIATION",
            "issue": "Missing aggregate liability cap or presence of uncapped/penalty language.",
            "authority": "Sections 73 & 74, ICA 1872; Kailash Nath Associates v. DDA, (2015) 4 SCC 136 (liquidated damages cannot operate as a punitive penalty; remote damages barred).",
            "redline": (
                "<<<< EXISTING / MISSING CLAUSE\n"
                "[Uncapped or unstated aggregate liability exposure]\n"
                "==== PLAYBOOK REPLACEMENT CLAUSE\n"
                "\"Notwithstanding anything to the contrary, neither Party's aggregate cumulative liability arising out of or related to this Agreement shall exceed 100% of the total fees paid in the twelve (12) months preceding the claim. Under no circumstances shall either Party be liable for indirect, special, incidental, or consequential damages under Section 73 of the Indian Contract Act, 1872.\"\n"
                ">>>>"
            ),
        })
    elif not has_consequential_waiver:
        findings.append({
            "pillar": "1. Limitation of Liability & Damages (Secs. 73 & 74, Indian Contract Act, 1872)",
            "severity": "MODERATE RISK",
            "issue": "Liability clause detected, but lacks an express exclusion of indirect/consequential loss of profits.",
            "authority": "Section 73, Indian Contract Act, 1872.",
            "redline": (
                "<<<< ADDENDUM TO LIABILITY CLAUSE\n"
                "==== INSERT AT END OF CLAUSE\n"
                "\"Neither Party shall be liable to the other for any indirect, remote, incidental, or consequential losses, including loss of profits or business interruption, under Section 73 of the Indian Contract Act, 1872.\"\n"
                ">>>>"
            ),
        })
    else:
        findings.append({
            "pillar": "1. Limitation of Liability & Damages (Secs. 73 & 74, Indian Contract Act, 1872)",
            "severity": "COMPLIANT",
            "issue": "Liability cap and consequential damage exclusions detected.",
            "authority": "Sections 73 & 74, Indian Contract Act, 1872.",
            "redline": "No redline required.",
        })

    # 2. Arbitration Neutrality & Jurisdiction (Sec. 12(5) A&C Act, 1996; CORE 2024 SC)
    unilateral_arb = any(
        k in lower
        for k in [
            "solely appointed by",
            "appointed by the company",
            "appointed by the lender",
            "panel curated by",
            "managing director shall appoint",
            "unilateral appointment",
        ]
    )
    has_bengaluru = any(k in lower for k in ["bengaluru", "bangalore", "karnataka"])

    if unilateral_arb or not has_bengaluru:
        issue_desc = []
        if unilateral_arb:
            issue_desc.append("Unilateral appointment of Sole Arbitrator / curated panel detected (Void ab initio).")
        if not has_bengaluru:
            issue_desc.append("Bengaluru / Karnataka seat and jurisdiction not explicitly specified.")
        findings.append({
            "pillar": "2. Arbitration Neutrality & Seat (Sec. 12(5) A&C Act, 1996)",
            "severity": "CRITICAL DEVIATION" if unilateral_arb else "HIGH RISK",
            "issue": " ".join(issue_desc),
            "authority": "Section 12(5) & Seventh Schedule, Arbitration & Conciliation Act, 1996; Perkins Eastman v. HSCC, (2020) 20 SCC 760; Central Organisation for Railway Electrification (CORE) v. ECI SPIC SMO MCML (JV), 2024 SCC OnLine SC 3219 (5-Judge Bench).",
            "redline": (
                "<<<< EXISTING DISPUTE RESOLUTION CLAUSE\n"
                "[Unilateral appointment / Non-Bengaluru Seat]\n"
                "==== PLAYBOOK REPLACEMENT CLAUSE\n"
                "\"Any dispute arising out of or in connection with this Agreement shall be referred to arbitration before a Sole Arbitrator appointed by mutual consent of the Parties, failing which under the rules of the Arbitration & Conciliation Centre – Bengaluru (Domestic & International). The seat and venue of arbitration shall be Bengaluru, Karnataka, and Courts at Bengaluru shall have exclusive jurisdiction.\"\n"
                ">>>>"
            ),
        })
    else:
        findings.append({
            "pillar": "2. Arbitration Neutrality & Seat (Sec. 12(5) A&C Act, 1996)",
            "severity": "COMPLIANT",
            "issue": "Bengaluru/Karnataka jurisdiction detected with no unilateral arbitrator appointment trigger.",
            "authority": "Section 12(5), Arbitration & Conciliation Act, 1996; CORE v. ECI SPIC (2024 SC).",
            "redline": "No redline required.",
        })

    # 3. Shortened Limitation Cut-Offs (Section 28, Indian Contract Act, 1872)
    short_limitation = re.search(
        r"(claim.{0,40}(barred|extinguished|waived).{0,40}(days|months))|(within\s+(15|30|60|90)\s+days.{0,30}forever\s+barred)",
        lower,
    )
    if short_limitation:
        findings.append({
            "pillar": "3. Bar Against Shortened Limitation (Section 28, Indian Contract Act, 1872)",
            "severity": "CRITICAL DEVIATION",
            "issue": "Clause attempts to curtail the statutory limitation period or extinguish rights prematurely.",
            "authority": "Section 28(a) & (b), Indian Contract Act, 1872 (Agreements restricting enforcement of rights within a shorter time than prescribed by the Limitation Act, 1963 are void).",
            "redline": (
                "<<<< VOID TIME-BAR CLAUSE\n"
                f"\"{short_limitation.group(0)}\"\n"
                "==== PLAYBOOK REPLACEMENT CLAUSE\n"
                "\"All claims and remedies under this Agreement shall be governed by the statutory limitation periods prescribed under the Limitation Act, 1963.\"\n"
                ">>>>"
            ),
        })
    else:
        findings.append({
            "pillar": "3. Bar Against Shortened Limitation (Section 28, Indian Contract Act, 1872)",
            "severity": "COMPLIANT",
            "issue": "No illegal curtailment of the 3-year statutory limitation period detected.",
            "authority": "Section 28, Indian Contract Act, 1872.",
            "redline": "No redline required.",
        })

    # 4. Post-Termination Restraint of Trade (Section 27, Indian Contract Act, 1872)
    has_non_compete = any(k in lower for k in ["non-compete", "non compete", "not engage in any competing", "shall not compete"])
    if has_non_compete:
        findings.append({
            "pillar": "4. Restraint of Trade & Non-Compete (Section 27, Indian Contract Act, 1872)",
            "severity": "HIGH RISK",
            "issue": "Non-compete restriction detected; post-termination restraint of trade is void in India.",
            "authority": "Section 27, Indian Contract Act, 1872; Percept D'Mark (India) Pvt. Ltd. v. Zaheer Khan, (2006) 4 SCC 227.",
            "redline": (
                "<<<< POST-TERMINATION NON-COMPETE\n"
                "[Restraint on trade/profession post-termination]\n"
                "==== PLAYBOOK REPLACEMENT CLAUSE\n"
                "\"During the Term of this Agreement, and for twelve (12) months thereafter strictly with respect to non-solicitation of direct employees and protection of Confidential Information, the Receiving Party shall not solicit key personnel or disclose proprietary trade secrets.\"\n"
                ">>>>"
            ),
        })
    else:
        findings.append({
            "pillar": "4. Restraint of Trade & Non-Compete (Section 27, Indian Contract Act, 1872)",
            "severity": "COMPLIANT",
            "issue": "No void post-termination restraint of trade detected.",
            "authority": "Section 27, Indian Contract Act, 1872.",
            "redline": "No redline required.",
        })

    # 5. Termination for Convenience & Determinability (Secs. 14(d) & 20, Specific Relief Act, 1963)
    has_termination_conv = any(k in lower for k in ["terminate for convenience", "without cause", "30 days' prior written notice", "thirty (30) days"])
    if not has_termination_conv:
        findings.append({
            "pillar": "5. Determinability & Specific Performance (Secs. 14(d) & 20, Specific Relief Act, 1963)",
            "severity": "MODERATE RISK",
            "issue": "No clear 'Termination for Convenience' clause detected; exposes party to mandatory specific performance injunctions under the 2018 Amendment to the Specific Relief Act.",
            "authority": "Section 14(d) & Section 20, Specific Relief Act, 1963 (as amended by Act 18 of 2018).",
            "redline": (
                "<<<< MISSING DETERMINABILITY CLAUSE\n"
                "==== INSERT TERMINATION FOR CONVENIENCE\n"
                "\"Either Party may terminate this Agreement for convenience without cause by providing thirty (30) days' prior written notice to the other Party, rendering this Agreement determinable within the meaning of Section 14(d) of the Specific Relief Act, 1963.\"\n"
                ">>>>"
            ),
        })
    else:
        findings.append({
            "pillar": "5. Determinability & Specific Performance (Secs. 14(d) & 20, Specific Relief Act, 1963)",
            "severity": "COMPLIANT",
            "issue": "Express termination notice clause detected, preserving determinability under Sec. 14(d) SRA.",
            "authority": "Section 14(d), Specific Relief Act, 1963.",
            "redline": "No redline required.",
        })

    # 6. Karnataka Stamp Duty & Admissibility (Karnataka Stamp Act, 1957 & Act 04 of 2024)
    has_stamp = any(k in lower for k in ["stamp duty", "e-stamp", "karnataka stamp act"])
    if not has_stamp:
        findings.append({
            "pillar": "6. Stamp Duty & Evidentiary Admissibility (Karnataka Stamp Act, 1957)",
            "severity": "MODERATE RISK",
            "issue": "No explicit stamp duty allocation clause detected.",
            "authority": "Articles 5(j) & 30 of Schedule, Sections 33 & 34, Karnataka Stamp Act, 1957 (as amended by Karnataka Act No. 04 of 2024 & Digital e-Stamp Rules, 2025 — ₹500 minimum stamp duty on general agreements; unstamped instruments face impounding + 10x penalty).",
            "redline": (
                "<<<< MISSING STAMP DUTY CLAUSE\n"
                "==== INSERT STAMP DUTY ALLOCATION\n"
                "\"Stamp duty payable on this Agreement under Article 5(j) of the Schedule to the Karnataka Stamp Act, 1957 (as amended by Karnataka Act No. 04 of 2024) shall be borne equally by the Parties via Digital e-Stamp prior to execution.\"\n"
                ">>>>"
            ),
        })
    else:
        findings.append({
            "pillar": "6. Stamp Duty & Evidentiary Admissibility (Karnataka Stamp Act, 1957)",
            "severity": "COMPLIANT",
            "issue": "Stamp duty allocation explicitly addressed.",
            "authority": "Karnataka Stamp Act, 1957 (Act 04 of 2024).",
            "redline": "No redline required.",
        })

    return findings


def review_contract(file_path):
    os.makedirs(REVIEW_OUT_DIR, exist_ok=True)

    # Support passing a directory (like ~/Downloads) to automatically pick the newest file
    if os.path.isdir(file_path):
        candidates = [
            os.path.join(file_path, f)
            for f in os.listdir(file_path)
            if os.path.isfile(os.path.join(file_path, f)) and not f.startswith(".")
        ]
        if not candidates:
            print(f"[Error] No files found in directory '{file_path}'.")
            return
        candidates.sort(key=os.path.getmtime, reverse=True)
        file_path = candidates[0]
        print(f"[Auto-Selected Newest File in Directory] -> {file_path}")

    if not os.path.exists(file_path):
        print(f"\n[Error] Contract file '{file_path}' not found.")
        recent = list_recent_download_contracts(5)
        if recent:
            print("\nRecent files in your ~/Downloads folder:")
            for idx, r in enumerate(recent, 1):
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(r)).strftime("%Y-%m-%d %H:%M")
                print(f"  {idx}. {r}  (Modified: {mtime})")
            print("\nTip: Run `python3 sweety.py legal review --latest` to audit #1 automatically.\n")
        return

    text, parser_used = extract_contract_text(file_path)
    today = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    base_name = os.path.basename(file_path)

    print("\n=== SweetyAI Enterprise Indian Contract Playbook Auditor ===")
    print(f"Target File   : {file_path}")
    print(f"Parser Engine : {parser_used}")
    print(f"Document Size : {len(text):,} characters")

    # Optional RAG enrichment if local vector server is active
    rag_note = "Offline Statutory Engine Active (ICA 1872 / SRA 1963 / A&C Act 1996 / Karnataka Stamp Act 1957)"
    try:
        resp = requests.post(
            f"{BASE_URL}/rag-chat",
            json={"message": f"Contract risk audit: {text[:400]}"},
            timeout=3,
        )
        if resp.status_code == 200:
            sources = resp.json().get("sources", [])
            if sources:
                rag_note = f"Synced with Local Vector Corpus ({', '.join(sources[:3])})"
    except Exception:
        pass

    findings = evaluate_indian_statutory_playbook(text)
    deviations = [f for f in findings if f["severity"] != "COMPLIANT"]

    report = f"""# SWEETYAI INDIAN STATUTORY CONTRACT REVIEW & REDLINE REPORT
**Target Document:** `{file_path}`
**Extraction Engine:** {parser_used} ({len(text):,} chars)
**Audit Timestamp:** {today}
**Playbook Standard:** Indian Commercial Playbook (ICA 1872, SRA 1963, A&C Act 1996, Karnataka Stamp Act 1957)
**Vector Grounding:** {rag_note}
**Overall Risk Summary:** `{len(deviations)} Deviation(s) Flagged out of 6 Statutory Pillars`

---

## I. EXECUTIVE CLAUSE-BY-CLAUSE AUDIT MATRIX

| Statutory Pillar | Status | Key Finding |
| :--- | :--- | :--- |
"""
    for f in findings:
        report += f"| **{f['pillar']}** | `{f['severity']}` | {f['issue']} |\n"

    report += "\n---\n\n## II. DETAILED STATUTORY ANALYSIS & READY-TO-PASTE REDLINES\n\n"
    for f in findings:
        report += f"### {f['pillar']}\n"
        report += f"- **Audit Status:** `{f['severity']}`\n"
        report += f"- **Finding:** {f['issue']}\n"
        report += f"- **Controlling Authority:** {f['authority']}\n"
        if f["redline"] != "No redline required.":
            report += f"- **Automated Fallback Redline:**\n```diff\n{f['redline']}\n```\n\n"
        else:
            report += "\n"

    slug = os.path.splitext(base_name)[0].replace(" ", "_")
    out_path = os.path.join(REVIEW_OUT_DIR, f"contract_audit_{slug}.md")
    with open(out_path, "w", encoding="utf-8") as out_f:
        out_f.write(report)

    print("\n" + report)
    print("=========================================================================")
    print(f"[Success] Full Contract Audit & Redline Report saved -> '{out_path}'")
    print(f"          (Run `python3 sweety.py export {out_path}` for A4 Court/Client HTML)")
    print("=========================================================================\n")


def handle_review_cli(argv):
    parser = argparse.ArgumentParser(
        prog="sweety legal review",
        description="Audit PDF, DOCX, TXT, or MD contracts against the 6-Pillar Indian Statutory Playbook.",
    )
    parser.add_argument("file", nargs="?", help="Path to contract file or directory")
    parser.add_argument("--latest", action="store_true", help="Automatically review the newest document in ~/Downloads")
    parser.add_argument("--list-downloads", action="store_true", help="List recent documents in ~/Downloads")
    args = parser.parse_args(argv)

    if args.list_downloads:
        recent = list_recent_download_contracts(10)
        print(f"\n=== Recent Documents in {DOWNLOADS_DIR} ===")
        for idx, r in enumerate(recent, 1):
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(r)).strftime("%Y-%m-%d %H:%M")
            size_kb = os.path.getsize(r) / 1024.0
            print(f"  {idx}. {r}  ({size_kb:.1f} KB | {mtime})")
        print("================================================\n")
        return

    if args.latest:
        recent = list_recent_download_contracts(1)
        if not recent:
            print(f"[Error] No documents found in {DOWNLOADS_DIR}")
            return
        print(f"[Auto-Selecting Latest Download] -> {recent[0]}")
        review_contract(recent[0])
    elif args.file:
        review_contract(args.file)
    else:
        parser.print_help()


if __name__ == "__main__":
    handle_review_cli(sys.argv[1:])
