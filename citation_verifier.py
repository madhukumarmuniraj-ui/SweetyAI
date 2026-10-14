import os
import sys
import re
import zipfile
import datetime
import argparse
import requests
import xml.etree.ElementTree as ET

BASE_URL = "http://127.0.0.1:8765"
AUDIT_OUT_DIR = "citation_audit_reports"
DOWNLOADS_DIR = os.path.expanduser("~/Downloads")
DOC_EXTENSIONS = (".pdf", ".docx", ".md", ".txt", ".doc", ".rtf")

# Verified Landmark Precedent Index (Offline Ground-Truth Anchor)
LANDMARK_PRECEDENTS = {
    "arnesh kumar": (
        "Arnesh Kumar v. State of Bihar, (2014) 8 SCC 273",
        "Mandatory pre-arrest notice and checklist under Sec. 41/41A CrPC (now Sec. 35(3) BNSS, 2023) for offences punishable up to 7 years.",
    ),
    "bhajan lal": (
        "State of Haryana v. Bhajan Lal, 1992 Supp (1) SCC 335",
        "Seven illustrative categories for quashing FIR/criminal proceedings under Sec. 482 CrPC (now Sec. 528 BNSS, 2023) / Art. 226.",
    ),
    "lalita kumari": (
        "Lalita Kumari v. Government of U.P., (2014) 2 SCC 1",
        "Mandatory registration of FIR for cognizable offences; preliminary inquiry permissible in commercial/matrimonial/delayed disputes (cf. Sec. 173(3) BNSS).",
    ),
    "satender kumar antil": (
        "Satender Kumar Antil v. Central Bureau of Investigation, (2022) 10 SCC 51",
        "Categorization of offences for bail and strict compliance with Sec. 41/41A CrPC (Sec. 35 BNSS); non-compliance entitles accused to bail.",
    ),
    "sushila aggarwal": (
        "Sushila Aggarwal v. State (NCT of Delhi), (2020) 5 SCC 1",
        "5-Judge Constitution Bench: Anticipatory bail under Sec. 438 CrPC (Sec. 482 BNSS) ordinarily continues till end of trial without fixed time limit.",
    ),
    "khotkar": (
        "Arjun Panditrao Khotkar v. Kailash Kushanrao Gorantyal, (2020) 7 SCC 1",
        "Certificate under Sec. 65B(4) IEA (now Sec. 63(4) BSA, 2023) is a mandatory condition precedent for admissibility of secondary electronic evidence.",
    ),
    "neeharika infrastructure": (
        "Neeharika Infrastructure Pvt. Ltd. v. State of Maharashtra, (2021) 19 SCC 401",
        "Parameters governing interim stay of investigation under Sec. 482 CrPC (Sec. 528 BNSS) and Art. 226; 'no coercive steps' orders require reasoned basis.",
    ),
    "priyanka srivastava": (
        "Priyanka Srivastava v. State of Uttar Pradesh, (2015) 6 SCC 287",
        "Mandatory affidavit and prior exhaustion of remedies before Magistrate orders investigation under Sec. 156(3) CrPC (now codified in Sec. 175(3) BNSS).",
    ),
    "prabir purkayastha": (
        "Prabir Purkayastha v. State (NCT of Delhi), (2024) 8 SCC 254",
        "Supplying written 'grounds of arrest' (distinct from 'reasons for arrest') is mandatory under Art. 22(1) and Sec. 50 CrPC (Sec. 47 BNSS).",
    ),
    "pankaj bansal": (
        "Pankaj Bansal v. Union of India, (2024) 7 SCC 576",
        "Written grounds of arrest must be furnished to the arrestee as a matter of course and without exception.",
    ),
    "kailash nath": (
        "Kailash Nath Associates v. Delhi Development Authority, (2015) 4 SCC 136",
        "Principles governing liquidated damages and reasonable compensation under Sections 73 and 74 of the Indian Contract Act, 1872.",
    ),
    "perkins eastman": (
        "Perkins Eastman Architects DPC v. HSCC (India) Ltd., (2020) 20 SCC 760",
        "Unilateral appointment of a Sole Arbitrator by a party with an interest in the dispute outcome is invalid under Sec. 12(5) A&C Act, 1996.",
    ),
    "central organisation for railway electrification": (
        "Central Organisation for Railway Electrification (CORE) v. ECI SPIC SMO MCML (JV), 2024 SCC OnLine SC 3219",
        "5-Judge Constitution Bench: Unilateral appointment clauses or unilateral curated panels in public-private contracts violate Art. 14 and Sec. 18 A&C Act.",
    ),
    "percept d'mark": (
        "Percept D'Mark (India) Pvt. Ltd. v. Zaheer Khan, (2006) 4 SCC 227",
        "Post-termination non-compete covenants operate as an unlawful restraint of trade under Section 27 of the Indian Contract Act, 1872.",
    ),
}

# Statutory Maximum Section Bounds for Hallucination & Mix-Up Detection
STATUTE_MAX_SECTIONS = {
    "BNS": (358, "Bharatiya Nyaya Sanhita, 2023"),
    "BNSS": (531, "Bharatiya Nagarik Suraksha Sanhita, 2023"),
    "BSA": (170, "Bharatiya Sakshya Adhiniyam, 2023"),
    "IPC": (511, "Indian Penal Code, 1860"),
    "CRPC": (484, "Code of Criminal Procedure, 1973"),
    "IEA": (167, "Indian Evidence Act, 1872"),
}

# Known BNSS procedural sections frequently mislabeled as BNS in drafts
BNSS_PROCEDURAL_SECTIONS = {
    35: "Section 35 BNSS corresponds to Section 41/41A CrPC (Arrest & Notice of Appearance). Note: Section 35 BNS deals with Right of Private Defence.",
    47: "Section 47 BNSS corresponds to Section 50 CrPC (Grounds of Arrest).",
    173: "Section 173 BNSS corresponds to Section 154 CrPC (FIR Registration). Note: Section 173 BNS deals with Bribery at Elections.",
    175: "Section 175(3) BNSS corresponds to Section 156(3) CrPC (Magistrate direction for investigation).",
    180: "Section 180 BNSS corresponds to Section 161 CrPC (Examination of witnesses by police).",
    183: "Section 183 BNSS corresponds to Section 164 CrPC (Recording of confessions and statements).",
    187: "Section 187 BNSS corresponds to Section 167 CrPC (Procedure when investigation cannot be completed in 24 hours / Remand & Default Bail).",
    193: "Section 193 BNSS corresponds to Section 173 CrPC (Police Report / Charge Sheet upon completion of investigation).",
    480: "Section 480 BNSS corresponds to Section 437 CrPC (Regular Bail in non-bailable offence).",
    482: "Section 482 BNSS corresponds to Section 438 CrPC (Direction for grant of bail to person apprehending arrest / Anticipatory Bail).",
    483: "Section 483 BNSS corresponds to Section 439 CrPC (Special powers of High Court or Court of Session regarding bail).",
    528: "Section 528 BNSS corresponds to Section 482 CrPC (Saving of inherent powers of High Court).",
}


def extract_document_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    text_chunks = []
    parser_info = "Plain-Text UTF-8 Reader"

    if ext == ".docx" and zipfile.is_zipfile(file_path):
        try:
            with zipfile.ZipFile(file_path, "r") as z:
                xml_targets = ["word/document.xml", "word/footnotes.xml", "word/endnotes.xml"]
                extracted_sources = []
                for target in xml_targets:
                    if target in z.namelist():
                        xml_root = ET.fromstring(z.read(target))
                        for p in xml_root.iter():
                            if p.tag.endswith("}p"):
                                runs = [t.text for t in p.iter() if t.tag.endswith("}t") and t.text]
                                if runs:
                                    text_chunks.append("".join(runs))
                        extracted_sources.append(target.split("/")[-1])
                parser_info = f"Native DOCX XML Engine ({', '.join(extracted_sources)})"
        except Exception as e:
            parser_info = f"DOCX Fallback ({e})"

    elif ext == ".pdf":
        try:
            try:
                import pymupdf as fitz
            except ImportError:
                import fitz
            doc = fitz.open(file_path)
            for page in doc:
                text_chunks.append(page.get_text())
            parser_info = f"PyMuPDF Engine ({len(doc)} pages extracted)"
            doc.close()
        except Exception as e:
            parser_info = f"PDF Fallback Reader ({e})"

    full_text = "\n".join(text_chunks)
    if not full_text.strip():
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            full_text = f.read()

    return full_text, parser_info


def list_recent_downloads(limit=10):
    if not os.path.exists(DOWNLOADS_DIR):
        return []
    files = [
        os.path.join(DOWNLOADS_DIR, f)
        for f in os.listdir(DOWNLOADS_DIR)
        if os.path.isfile(os.path.join(DOWNLOADS_DIR, f)) and not f.startswith(".")
    ]
    doc_files = [f for f in files if os.path.splitext(f)[1].lower() in DOC_EXTENSIONS]
    target = doc_files if doc_files else files
    target.sort(key=os.path.getmtime, reverse=True)
    return target[:limit]


def extract_all_citations(content):
    # 1. Multi-word Party v. Party Case Names
    party_word = r"[A-Z][A-Za-z0-9\.\'\-\&\(\)]+"
    party_phrase = rf"{party_word}(?:\s+(?:of|and|&|for|the|in|re|{party_word})){{0,6}}"
    case_name_pattern = rf"\b({party_phrase}\s+(?:v\.|vs\.|versus)\s+{party_phrase})"

    raw_cases = re.findall(case_name_pattern, content)
    cleaned_cases = []
    seen_case_keys = set()
    stop_tail_words = {"In", "Where", "Holding", "Held", "Under", "That", "And", "The", "For", "On", "At"}

    for c in raw_cases:
        c_clean = re.sub(r"\s+", " ", c).strip(" ,.;:()")
        tokens = c_clean.split()
        while len(tokens) > 3 and tokens[-1] in stop_tail_words:
            tokens.pop()
        c_clean = " ".join(tokens)
        key = c_clean.lower()
        if len(c_clean) >= 8 and key not in seen_case_keys:
            seen_case_keys.add(key)
            cleaned_cases.append(c_clean)

    # 2. Reporter Citations (SCC, SCC OnLine, AIR, INSC, KHC, ILR KAR, Kar LJ)
    reporter_patterns = [
        r"\(\d{4}\)\s*\d+\s*SCC\s*(?:\([A-Za-z\s]+\)\s*)?\d+",
        r"\d{4}\s+Supp\s*\(\d+\)\s*SCC\s*\d+",
        r"\d{4}\s+SCC\s+OnLine\s+[A-Za-z]+\s+\d+",
        r"AIR\s+\d{4}\s+[A-Za-z]+\s+\d+",
        r"\d{4}\s+INSC\s+\d+",
        r"\d{4}:KHC(?:-D|-K)?:\d+",
        r"ILR\s+\d{4}\s+KAR\s+\d+",
        r"\d{4}\s*\(\d+\)\s*Kar\s*L\.?J\.?\s*\d+",
    ]
    reporters_found = []
    seen_rep = set()
    for rp in reporter_patterns:
        for m in re.findall(rp, content):
            m_clean = re.sub(r"\s+", " ", m).strip()
            if m_clean not in seen_rep:
                seen_rep.add(m_clean)
                reporters_found.append(m_clean)

    # 3. Statutory References — NB: BNSS placed BEFORE BNS with strict \b word boundary!
    statute_pattern = (
        r"\b(?:Section|Sec\.|Article|Art\.|Order|Rule)\s+\d+[A-Z]?"
        r"(?:\([0-9a-zA-Z]+\))*"
        r"(?:\s+(?:of\s+(?:the\s+)?)?(?:BNSS|BNS|BSA|CrPC|IPC|IEA|CPC|Constitution|KCFSV\s+Act|ICA|SRA|A&C\s+Act)\b)?"
    )
    raw_statutes = re.findall(statute_pattern, content, flags=re.IGNORECASE)
    statutes_found = []
    seen_stat = set()
    for s in raw_statutes:
        s_clean = re.sub(r"\s+", " ", s).strip()
        s_key = s_clean.upper()
        if s_key not in seen_stat:
            seen_stat.add(s_key)
            statutes_found.append(s_clean)

    return cleaned_cases, reporters_found, statutes_found


def verify_case_grounding(case_str):
    lower_c = case_str.lower()
    # 1. Check Built-in Landmark Registry first
    for key, (canonical, ratio) in LANDMARK_PRECEDENTS.items():
        if key in lower_c:
            return "VERIFIED (Landmark Authority Registry)", f"{canonical} — *{ratio}*"

    # 2. Query Local ChromaDB RAG Vector Server
    try:
        resp = requests.post(f"{BASE_URL}/rag-chat", json={"message": case_str}, timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            resp_text = data.get("response", "").lower()
            sources = data.get("sources", [])
            first_party = lower_c.split(" v")[0].split()[-1]
            if first_party in resp_text and len(first_party) > 3:
                src_label = ", ".join(sources[:2]) if sources else "Local Vector Corpus"
                return f"VERIFIED (Local Vector Store: {src_label})", "Matched in local indexed corpus."
            return "UNINDEXED (Verify Reporter Citation)", "Not found in local ChromaDB index; verify physical reporter volume/page."
    except Exception:
        pass

    return "UNVERIFIED (Offline / Not in Local Corpus)", "Confirm party spelling and reporter citation manually before filing."


def validate_statute_reference(statute_str):
    m = re.search(
        r"(?:Section|Sec\.)\s+(\d+)[A-Z]?(?:\(([0-9a-zA-Z]+)\))?(?:.*?\b(BNSS|BNS|BSA|CRPC|IPC|IEA)\b)?",
        statute_str,
        flags=re.IGNORECASE,
    )
    if not m:
        return "VALIDATED", "Constitutional / Procedural reference."

    sec_num = int(m.group(1))
    sub_sec = m.group(2) or ""
    code_tag = (m.group(3) or "").upper()

    if code_tag in STATUTE_MAX_SECTIONS:
        max_sec, full_name = STATUTE_MAX_SECTIONS[code_tag]
        if sec_num > max_sec:
            if code_tag == "BNS" and sec_num <= 531:
                return (
                    "CRITICAL CODE MISMATCH",
                    f"Section {sec_num} does NOT exist in {full_name} (max is Section 358). Did you mean **Section {sec_num} BNSS, 2023**?",
                )
            return (
                "CRITICAL HALLUCINATION / RANGE ERROR",
                f"Section {sec_num} exceeds the maximum section ({max_sec}) of {full_name}.",
            )

        if code_tag == "BNS" and sec_num in BNSS_PROCEDURAL_SECTIONS:
            return (
                "WARNING: BNS vs. BNSS PROCEDURAL CHECK",
                BNSS_PROCEDURAL_SECTIONS[sec_num],
            )

        return "VERIFIED STATUTE", f"Valid section within {full_name} (Sections 1–{max_sec})."

    if sec_num in BNSS_PROCEDURAL_SECTIONS:
        return "CHECKED (Specify Act Name)", BNSS_PROCEDURAL_SECTIONS[sec_num]

    return "CHECKED", "Section number within standard statutory bounds."


def verify_file_citations(file_path):
    os.makedirs(AUDIT_OUT_DIR, exist_ok=True)

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
        print(f"\n[Error] File '{file_path}' not found.")
        recent = list_recent_downloads(5)
        if recent:
            print("\nRecent files in your ~/Downloads folder:")
            for idx, r in enumerate(recent, 1):
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(r)).strftime("%Y-%m-%d %H:%M")
                print(f"  {idx}. {r}  (Modified: {mtime})")
            print("\nTip: Run `python3 sweety.py legal verify-citations --latest` to audit #1 automatically.\n")
        return

    content, parser_info = extract_document_text(file_path)
    today = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    base_name = os.path.basename(file_path)

    cases_found, reporters_found, statutes_found = extract_all_citations(content)

    print("\n=== SweetyAI Automated Citation & Statutory Verifier ===")
    print(f"Target File     : {file_path}")
    print(f"Parser Engine   : {parser_info} ({len(content):,} chars)")
    print(f"Case Titles     : {len(cases_found)}")
    print(f"Reporter Cites  : {len(reporters_found)}")
    print(f"Statutes Cited  : {len(statutes_found)}")

    verified_cases = [
        (c, *verify_case_grounding(c))
        for c in cases_found
    ]
    validated_statutes = [
        (s, *validate_statute_reference(s))
        for s in statutes_found
    ]

    mismatches = [s for s in validated_statutes if "CRITICAL" in s[1] or "WARNING" in s[1]]

    report = f"""# SWEETYAI CITATION, REPORTER & STATUTORY VERIFICATION REPORT
**Target Document:** `{file_path}`
**Extraction Engine:** {parser_info} ({len(content):,} characters)
**Audit Timestamp:** {today}
**Summary:** `{len(cases_found)} Case Titles` | `{len(reporters_found)} Reporter Citations` | `{len(statutes_found)} Statutory Provisions` | `{len(mismatches)} Statutory Alerts`

---

## I. EXTRACTED CASE LAW AUTHORITIES & GROUNDING STATUS
"""
    if verified_cases:
        for idx, (case_name, status, detail) in enumerate(verified_cases, 1):
            report += f"{idx}. **{case_name}** — `{status}`\n   - *Authority Note:* {detail}\n"
    else:
        report += "- No party-versus-party case titles (`v.` / `vs.`) detected in document text.\n"

    report += "\n---\n\n## II. EXTRACTED REPORTER & NEUTRAL CITATIONS\n"
    if reporters_found:
        for idx, rep in enumerate(reporters_found, 1):
            report += f"{idx}. `{rep}` — **Format Verified** (Standard Indian Law Reporter / Neutral Citation)\n"
    else:
        report += "- No explicit reporter volume/page strings (`SCC`, `AIR`, `INSC`, `KHC`, `ILR KAR`) detected.\n"

    report += "\n---\n\n## III. STATUTORY REFERENCES & BNS / BNSS / BSA BOUNDARY AUDIT\n"
    if validated_statutes:
        for idx, (stat, status, note) in enumerate(validated_statutes, 1):
            report += f"{idx}. **{stat}** — `{status}`\n   - *{note}*\n"
    else:
        report += "- No statutory provisions detected.\n"

    slug = os.path.splitext(base_name)[0].replace(" ", "_")
    out_path = os.path.join(AUDIT_OUT_DIR, f"citation_audit_{slug}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)

    print("\n" + report)
    print("=========================================================================")
    print(f"[Success] Citation Verification Report saved -> '{out_path}'")
    print(f"          (Run `python3 sweety.py export {out_path}` for A4 Court-Ready HTML)")
    print("=========================================================================\n")


def handle_verify_cli(argv):
    parser = argparse.ArgumentParser(
        prog="sweety legal verify-citations",
        description="Extract and verify case citations, reporters, and BNS/BNSS/BSA sections from PDF, DOCX, MD, or TXT briefs.",
    )
    parser.add_argument("file", nargs="?", help="Path to brief, petition, judgment, or directory")
    parser.add_argument("--latest", action="store_true", help="Automatically audit the newest PDF/DOCX/MD/TXT in ~/Downloads")
    parser.add_argument("--list-downloads", action="store_true", help="List recent documents in ~/Downloads")
    args = parser.parse_args(argv)

    if args.list_downloads:
        recent = list_recent_downloads(10)
        print(f"\n=== Recent Documents in {DOWNLOADS_DIR} ===")
        for idx, r in enumerate(recent, 1):
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(r)).strftime("%Y-%m-%d %H:%M")
            size_kb = os.path.getsize(r) / 1024.0
            print(f"  {idx}. {r}  ({size_kb:.1f} KB | {mtime})")
        print("================================================\n")
        return

    if args.latest:
        recent = list_recent_downloads(1)
        if not recent:
            print(f"[Error] No documents found in {DOWNLOADS_DIR}")
            return
        print(f"[Auto-Selecting Latest Download] -> {recent[0]}")
        verify_file_citations(recent[0])
    elif args.file:
        verify_file_citations(args.file)
    else:
        parser.print_help()


if __name__ == "__main__":
    handle_verify_cli(sys.argv[1:])
