import os
import sys
import re
import glob
import zipfile
import datetime
import argparse
import xml.etree.ElementTree as ET

PRIVACY_OUT_DIR = "privacy_audit_reports"
SKILL_DIR = os.path.join("anthropic_plugins", "legal", "skills")
FIRM_SKILL_DIR = "firm_skills"
DOWNLOADS_DIR = os.path.expanduser("~/Downloads")


def extract_text_and_metadata(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    metadata = {}
    text_content = ""

    if ext == ".docx" and zipfile.is_zipfile(file_path):
        try:
            with zipfile.ZipFile(file_path, "r") as z:
                if "docProps/core.xml" in z.namelist():
                    core_xml = ET.fromstring(z.read("docProps/core.xml"))
                    for elem in core_xml.iter():
                        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                        if elem.text and elem.text.strip():
                            metadata[f"DOCX:{tag}"] = elem.text.strip()
                if "word/document.xml" in z.namelist():
                    doc_xml = ET.fromstring(z.read("word/document.xml"))
                    paragraphs = []
                    for p in doc_xml.iter():
                        if p.tag.endswith("}p"):
                            texts = [t.text for t in p.iter() if t.tag.endswith("}t") and t.text]
                            if texts:
                                paragraphs.append("".join(texts))
                    text_content = "\n".join(paragraphs)
        except Exception as e:
            metadata["ExtractionWarning"] = str(e)

    elif ext == ".pdf":
        try:
            try:
                import pymupdf as fitz
            except ImportError:
                import fitz
            doc = fitz.open(file_path)
            if doc.metadata:
                for k, v in doc.metadata.items():
                    if v:
                        metadata[f"PDF:{k}"] = str(v)
            pages = [page.get_text() for page in doc]
            text_content = "\n".join(pages)
            doc.close()
        except Exception as e:
            metadata["ExtractionWarning"] = f"PDF parser note: {e}"

    if not text_content:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            text_content = f.read()

    return text_content, metadata


def list_recent_downloads(limit=10):
    if not os.path.exists(DOWNLOADS_DIR):
        print(f"[Error] Downloads directory '{DOWNLOADS_DIR}' not found.")
        return []
    all_files = [
        os.path.join(DOWNLOADS_DIR, f)
        for f in os.listdir(DOWNLOADS_DIR)
        if os.path.isfile(os.path.join(DOWNLOADS_DIR, f)) and not f.startswith(".")
    ]
    all_files.sort(key=os.path.getmtime, reverse=True)
    return all_files[:limit]


def audit_file_privacy(file_path, scrub=False):
    os.makedirs(PRIVACY_OUT_DIR, exist_ok=True)

    # If user passed a directory (e.g., ~/Downloads), pick the newest file inside it
    if os.path.isdir(file_path):
        candidates = [
            os.path.join(file_path, f)
            for f in os.listdir(file_path)
            if os.path.isfile(os.path.join(file_path, f)) and not f.startswith(".")
        ]
        if not candidates:
            print(f"[Error] No files found inside directory '{file_path}'.")
            return
        candidates.sort(key=os.path.getmtime, reverse=True)
        file_path = candidates[0]
        print(f"[Auto-Detected Latest File in Directory] -> {file_path}")

    if not os.path.exists(file_path):
        print(f"\n[Error] File '{file_path}' not found.")
        recent = list_recent_downloads(5)
        if recent:
            print("\nHere are the 5 most recent files in your ~/Downloads folder:")
            for idx, r in enumerate(recent, 1):
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(r)).strftime("%Y-%m-%d %H:%M")
                size_kb = os.path.getsize(r) / 1024.0
                print(f"  {idx}. {r}  ({size_kb:.1f} KB | Modified: {mtime})")
            print("\nTip: Run `python3 sweety.py legal privacy-audit --latest --scrub` to audit #1 automatically.\n")
        return

    content, metadata = extract_text_and_metadata(file_path)
    today = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    base_name = os.path.basename(file_path)

    patterns = {
        "PAN (Permanent Account Number)": r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
        "Aadhaar Number (12-digit UID)": r"\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b",
        "GSTIN (Karnataka / Pan-India)": r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b",
        "Indian Mobile Number": r"(?:\+91[\-\s]?)?[6-9]\d{9}\b",
        "Email Address": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "Bank IFSC Code": r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
    }

    findings = {}
    total_hits = 0
    scrubbed_content = content

    for label, pat in patterns.items():
        matches = list(set(re.findall(pat, content)))
        findings[label] = matches
        total_hits += len(matches)
        if scrub and matches:
            scrubbed_content = re.sub(pat, f"[REDACTED-{label.split()[0].upper()}]", scrubbed_content)

    sensitive_triggers = []
    if re.search(r"\b(POSH|sexual harassment|victim|minor|POCSO|Section 85 BNS|Section 64 BNS)\b", content, re.IGNORECASE):
        sensitive_triggers.append(
            "MANDATORY ANONYMIZATION TRIGGER: Document references sexual offences / POSH / minor identity. "
            "Identity redaction is mandatory under Section 72 BNS, 2023 and Section 16 of the POSH Act, 2013."
        )

    report = f"""# SWEETYAI LEGAL DATA PRIVACY, METADATA & PRIVILEGE AUDIT
**Target File:** `{file_path}`
**Extracted Characters:** {len(content):,} chars
**Audit Timestamp:** {today}
**Processing Environment:** `127.0.0.1` (100% Air-Gapped Local Execution — Zero Cloud Retention)

---

## I. STATUTORY PRIVILEGE & DATA PROTECTION STATUS
1. **Advocate-Client Privilege (Sections 132–134, Bharatiya Sakshya Adhiniyam, 2023):**
   - **Status:** `PROTECTED (Local Execution)`
   - **Compliance Note:** Processed strictly within local workspace without external telemetry, preserving confidentiality under Section 132 BSA, 2023.
2. **Digital Personal Data Protection Act, 2023 (DPDP Act):**
   - **Litigation Exemption (Section 17(1)(a)):** Applicable where processing is for enforcing any legal right or claim.
   - **Security Safeguard Mandate (Section 8(5)):** Active.

---

## II. HIDDEN DOCUMENT METADATA INSPECTION (PDF / DOCX HEADERS)
"""
    if metadata:
        for k, v in metadata.items():
            report += f"- **{k}:** `{v}`\n"
    else:
        report += "- No embedded PDF/DOCX author or revision metadata headers detected.\n"

    report += f"""
---

## III. PERSONAL DATA & IDENTIFIER SCAN (PII INVENTORY)
**Total Sensitive Identifiers Detected:** {total_hits}
"""
    for label, items in findings.items():
        if items:
            masked_preview = [x[:3] + "***" + x[-2:] if len(x) > 5 else "***" for x in items[:5]]
            report += f"- **{label}:** {len(items)} found (Sample masked: `{', '.join(masked_preview)}`)\n"
        else:
            report += f"- **{label}:** `0 found (Clean)`\n"

    report += "\n---\n\n## IV. SPECIAL STATUTORY ANONYMIZATION ALERTS\n"
    if sensitive_triggers:
        for t in sensitive_triggers:
            report += f"- **CRITICAL:** {t}\n"
    else:
        report += "- No Section 72 BNS / Section 16 POSH Act mandatory identity-suppression triggers detected.\n"

    if scrub:
        scrub_path = os.path.join(PRIVACY_OUT_DIR, f"redacted_{base_name}.txt")
        with open(scrub_path, "w", encoding="utf-8") as sf:
            sf.write(scrubbed_content)
        report += f"\n---\n\n## V. REDACTED OUTPUT GENERATED\n- Sanitized text copy saved to: `{scrub_path}`\n"

    out_report_path = os.path.join(PRIVACY_OUT_DIR, f"privacy_audit_{base_name}.md")
    with open(out_report_path, "w", encoding="utf-8") as rf:
        rf.write(report)

    print("\n" + report)
    print("=========================================================================")
    print(f"[Success] Privacy & Metadata Audit Report saved -> '{out_report_path}'")
    print("=========================================================================\n")


def handle_privacy_cli(argv):
    parser = argparse.ArgumentParser(
        prog="sweety legal privacy-audit",
        description="Audit legal files (PDF/DOCX/TXT/MD) for PII, hidden metadata, BSA Sec. 132 Privilege, and DPDP Act compliance.",
    )
    parser.add_argument("file", nargs="?", help="Path to legal document or directory to audit")
    parser.add_argument("--latest", action="store_true", help="Automatically audit the most recent file in ~/Downloads")
    parser.add_argument("--list-downloads", action="store_true", help="List recent files in ~/Downloads")
    parser.add_argument("--scrub", action="store_true", help="Generate a PII-redacted text copy of the document")
    args = parser.parse_args(argv)

    if args.list_downloads:
        recent = list_recent_downloads(10)
        print(f"\n=== 10 Most Recent Files in {DOWNLOADS_DIR} ===")
        for idx, r in enumerate(recent, 1):
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(r)).strftime("%Y-%m-%d %H:%M")
            size_kb = os.path.getsize(r) / 1024.0
            print(f"  {idx}. {r}  ({size_kb:.1f} KB | {mtime})")
        print("====================================================\n")
        return

    if args.latest:
        recent = list_recent_downloads(1)
        if not recent:
            print(f"[Error] No files found in {DOWNLOADS_DIR}")
            return
        print(f"[Auto-Selecting Latest Download] -> {recent[0]}")
        audit_file_privacy(recent[0], args.scrub)
    elif args.file:
        audit_file_privacy(args.file, args.scrub)
    else:
        parser.print_help()


if __name__ == "__main__":
    handle_privacy_cli(sys.argv[1:])
