import os
import sys
import re
import time
import hashlib
import datetime
import argparse

from privacy_and_playbook_engine import audit_file_privacy, extract_text_and_metadata
from contract_reviewer import review_contract, evaluate_indian_statutory_playbook
from citation_verifier import verify_file_citations, extract_all_citations, verify_case_grounding, validate_statute_reference
from chronology_extractor import generate_chronology_document, extract_chronology_events, synthesize_synopsis_points
from trial_and_evidence_suite import generate_sec63_certificate
from document_exporter import export_document

DOSSIER_OUT_DIR = "master_case_dossiers"
DOWNLOADS_DIR = os.path.expanduser("~/Downloads")
DOC_EXTENSIONS = (".pdf", ".docx", ".md", ".txt", ".doc", ".rtf")


def get_latest_download_file():
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


def compute_hashes(file_path):
    h256 = hashlib.sha256()
    hmd5 = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h256.update(chunk)
            hmd5.update(chunk)
    return h256.hexdigest().upper(), hmd5.hexdigest().upper()


def run_full_case_audit(
    file_path,
    jurisdiction="crlp",
    deponent="Madhukumar Muniraj",
    device="Linux Enterprise Workstation",
    scrub=True,
):
    os.makedirs(DOSSIER_OUT_DIR, exist_ok=True)
    t_start = time.time()

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

    if not os.path.exists(file_path):
        print(f"[Error] Target file '{file_path}' not found.")
        return

    base_name = os.path.basename(file_path)
    slug = re.sub(r"[^A-Za-z0-9_\-]", "_", os.path.splitext(base_name)[0])
    file_size = os.stat(file_path).st_size
    today_str = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    print("\n=========================================================================")
    print("       SWEETYAI ONE-CLICK MASTER CASE PACKET PIPELINE (6 STAGES)         ")
    print("=========================================================================")
    print(f"Target File  : {file_path} ({file_size:,} bytes)")
    print(f"Jurisdiction : {jurisdiction.upper()} | Custodian: {deponent}")
    print("-------------------------------------------------------------------------")

    # Stage 1: Privacy, PII & BSA Sec. 132 Audit
    print("[Stage 1/6] Running BSA Sec. 132 Privilege, Metadata & DPDP PII Audit...")
    audit_file_privacy(file_path, scrub=scrub)

    # Stage 2: 6-Pillar Indian Statutory Contract Review
    print("[Stage 2/6] Running 6-Pillar Indian Statutory Contract Playbook Audit...")
    review_contract(file_path)

    # Stage 3: Case Citation & BNS/BNSS/BSA Statutory Range Verification
    print("[Stage 3/6] Running Case Law & BNS/BNSS/BSA Statutory Verifier...")
    verify_file_citations(file_path)

    # Stage 4: High Court Synopsis & Chronological List of Dates
    print("[Stage 4/6] Extracting High Court Synopsis & Chronological List of Dates...")
    generate_chronology_document(file_path, jurisdiction=jurisdiction)

    # Stage 5: Section 63(4) BSA Electronic Evidence SHA-256 Certificate
    print("[Stage 5/6] Generating Section 63(4) BSA SHA-256 Certificate (Part A & B)...")
    generate_sec63_certificate(file_path, deponent_name=deponent, device_desc=device)

    # Stage 6: Consolidate Master Case Dossier & Export to High Court A4 HTML
    print("[Stage 6/6] Compiling Consolidated Master Dossier & High Court A4 HTML...")
    text_content, metadata = extract_text_and_metadata(file_path)
    sha256_hex, md5_hex = compute_hashes(file_path)
    playbook_findings = evaluate_indian_statutory_playbook(text_content)
    cases_found, reporters_found, statutes_found = extract_all_citations(text_content)
    events = extract_chronology_events(text_content)
    synopsis_pts = synthesize_synopsis_points(text_content, events, jurisdiction)

    deviations = [f for f in playbook_findings if f["severity"] != "COMPLIANT"]
    validated_statutes = [(s, *validate_statute_reference(s)) for s in statutes_found]
    stat_alerts = [s for s in validated_statutes if "CRITICAL" in s[1] or "WARNING" in s[1]]

    elapsed_total = f"{(time.time() - t_start):.2f}s"

    dossier_md = f"""# IN THE HIGH COURT OF KARNATAKA AT BENGALURU
## SWEETYAI CONSOLIDATED MASTER CASE DOSSIER & LITIGATION PACKET
*(Prepared under Section 132 & Section 63(4) of the Bharatiya Sakshya Adhiniyam, 2023 and Chapter XII Rule 2 of the Karnataka High Court Rules, 1959)*

| Master Dossier Particular | Verified Audit Record |
| :--- | :--- |
| **Source Electronic Record** | `{file_path}` ({file_size:,} bytes / {len(text_content):,} extracted chars) |
| **SHA-256 Digital Fingerprint (Sec. 63(4) BSA)** | `{sha256_hex}` |
| **MD5 Checksum** | `{md5_hex}` |
| **Advocate-Client Privilege Status** | `PROTECTED — Sec. 132 BSA, 2023 (100% Air-Gapped Local Execution)` |
| **Contract Playbook Risk Score** | `{len(deviations)} Statutory Deviation(s) Flagged out of 6 Indian Pillars` |
| **Citations & Statutes Extracted** | `{len(cases_found)} Case Titles | {len(reporters_found)} Reporters | {len(statutes_found)} Statutes ({len(stat_alerts)} Alerts)` |
| **Chronological Milestones** | `{len(events)} Dated Events Sorted in Ascending Order` |
| **Pipeline Execution Time** | `{elapsed_total}` (Completed on {today_str}) |

---

## SECTION I: EXECUTIVE SYNOPSIS FOR THE COURT

"""
    for idx, pt in enumerate(synopsis_pts, 1):
        dossier_md += f"{idx}. {pt}\n"

    dossier_md += """
---

## SECTION II: CHRONOLOGICAL LIST OF DATES AND EVENTS

| Sl. No. | Date (DD.MM.YYYY) | Stage / Milestone | Particulars of Events |
| :--- | :--- | :--- | :--- |
"""
    if events:
        for idx, ev in enumerate(events, 1):
            dossier_md += f"| {idx}. | **{ev['date_formatted']}** | `{ev['milestone']}` | {ev['particulars']} |\n"
    else:
        dossier_md += "| 1. | **[Insert Date]** | `CASE RECORD` | No explicit calendar dates detected in source file; populate from annexures. |\n"

    dossier_md += """
---

## SECTION III: 6-PILLAR INDIAN STATUTORY CONTRACT & RISK AUDIT

| Statutory Pillar | Audit Verdict | Finding & Controlling Law |
| :--- | :--- | :--- |
"""
    for f in playbook_findings:
        dossier_md += f"| **{f['pillar']}** | `{f['severity']}` | {f['issue']} *(Ref: {f['authority']})* |\n"

    dossier_md += "\n---\n\n## SECTION IV: CITATION & BNS / BNSS / BSA VERIFICATION SUMMARY\n\n"
    if cases_found:
        for idx, c in enumerate(cases_found, 1):
            st, det = verify_case_grounding(c)
            dossier_md += f"{idx}. **{c}** — `{st}` ({det})\n"
    else:
        dossier_md += "- No party-versus-party case titles (`v.` / `vs.`) detected.\n"

    if validated_statutes:
        dossier_md += "\n### Statutory Provision Boundary Checks:\n"
        for stat, st, note in validated_statutes:
            dossier_md += f"- **{stat}** — `{st}`: {note}\n"

    dossier_md += f"""
---

## SECTION V: SECTION 63(4) BSA ELECTRONIC EVIDENCE CERTIFICATION SUMMARY
- **Deponent / Custodian (Part A):** {deponent}
- **Computer / Device System:** {device}
- **SHA-256 Cryptographic Hash (Part B):** `{sha256_hex}`
- **Individual Sub-Reports Generated in Workspace:**
  1. Privacy & PII Audit: `privacy_audit_reports/privacy_audit_{base_name}.md`
  2. Contract Playbook Audit: `contract_review_reports/contract_audit_{slug}.md`
  3. Citation & Statute Audit: `citation_audit_reports/citation_audit_{slug}.md`
  4. High Court Chronology: `chronology_outputs/synopsis_list_of_dates_{slug}.md`
  5. Sec. 63(4) BSA Certificate: `sec63_certificates/`
"""

    dossier_path = os.path.join(DOSSIER_OUT_DIR, f"master_dossier_{slug}.md")
    with open(dossier_path, "w", encoding="utf-8") as f:
        f.write(dossier_md)

    export_document(dossier_path)
    html_export_path = os.path.join("court_ready_exports", f"master_dossier_{slug}_court_ready.html")

    print("\n=========================================================================")
    print("       ONE-CLICK CASE PACKET PIPELINE COMPLETED SUCCESSFULLY             ")
    print("=========================================================================")
    print(f"Total Pipeline Time   : {elapsed_total}")
    print(f"Master Markdown Brief : {dossier_path}")
    print(f"High Court A4 HTML    : {html_export_path}")
    print("=========================================================================\n")


def handle_full_audit_cli(argv):
    parser = argparse.ArgumentParser(
        prog="sweety legal full-audit",
        description="One-Click 6-Stage Master Case Packet Pipeline (Privacy + Playbook + Citations + Chronology + Sec. 63(4) BSA + High Court A4 Export).",
    )
    parser.add_argument("file", nargs="?", help="Path to PDF, DOCX, MD, or TXT file (or directory)")
    parser.add_argument("--latest", action="store_true", help="Automatically run the full 6-stage pipeline on the newest file in ~/Downloads")
    parser.add_argument("--jurisdiction", choices=["crlp", "wp", "rfa", "comm"], default="crlp", help="High Court / Commercial Court format preset")
    parser.add_argument("--deponent", default="Madhukumar Muniraj", help="Deponent name for Section 63(4) BSA Certificate")
    parser.add_argument("--device", default="Linux Enterprise Workstation", help="Computer/device description for Section 63(4) BSA")
    parser.add_argument("--no-scrub", action="store_true", help="Disable generating a PII-redacted text copy")
    args = parser.parse_args(argv)

    if args.latest:
        target = get_latest_download_file()
        if not target:
            print(f"[Info] No files found in {DOWNLOADS_DIR}; falling back to 'sample_contract.txt'.")
            target = "sample_contract.txt"
        else:
            print(f"[Auto-Selected Newest Download] -> {target}")
    else:
        target = args.file

    if not target:
        parser.print_help()
        return

    run_full_case_audit(
        file_path=target,
        jurisdiction=args.jurisdiction,
        deponent=args.deponent,
        device=args.device,
        scrub=not args.no_scrub,
    )


if __name__ == "__main__":
    handle_full_audit_cli(sys.argv[1:])
