import os
import sys
import re
import zipfile
import datetime
import argparse
import xml.etree.ElementTree as ET

CHRONOLOGY_OUT_DIR = "chronology_outputs"
DOWNLOADS_DIR = os.path.expanduser("~/Downloads")
DOC_EXTENSIONS = (".pdf", ".docx", ".md", ".txt", ".doc", ".rtf")

JURISDICTION_HEADERS = {
    "crlp": {
        "court": "IN THE HIGH COURT OF KARNATAKA AT BENGALURU",
        "case_no": "CRL.P. No. ____________ / 2026",
        "provision": "(Under Section 528 of the Bharatiya Nagarik Suraksha Sanhita, 2023)",
        "party_a": "PETITIONER / ACCUSED",
        "party_b": "RESPONDENT / STATE & COMPLAINANT",
    },
    "wp": {
        "court": "IN THE HIGH COURT OF KARNATAKA AT BENGALURU",
        "case_no": "W.P. No. ____________ / 2026 (GM-RES)",
        "provision": "(Under Articles 226 and 227 of the Constitution of India)",
        "party_a": "PETITIONER",
        "party_b": "RESPONDENTS",
    },
    "rfa": {
        "court": "IN THE HIGH COURT OF KARNATAKA AT BENGALURU",
        "case_no": "R.F.A. No. ____________ / 2026",
        "provision": "(Under Section 96 read with Order XLI Rule 1 of the Code of Civil Procedure, 1908)",
        "party_a": "APPELLANT",
        "party_b": "RESPONDENT",
    },
    "comm": {
        "court": "IN THE COURT OF THE LXXXII ADDL. CITY CIVIL & SESSIONS JUDGE (COMMERCIAL COURT) AT BENGALURU (CCH-83)",
        "case_no": "COM.O.S. No. ____________ / 2026",
        "provision": "(Under Section 2(1)(c) read with Section 6 of the Commercial Courts Act, 2015)",
        "party_a": "PLAINTIFF",
        "party_b": "DEFENDANT",
    },
}

MONTH_MAP = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}


def extract_document_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    text_chunks = []
    parser_info = "Plain-Text UTF-8 Reader"

    if ext == ".docx" and zipfile.is_zipfile(file_path):
        try:
            with zipfile.ZipFile(file_path, "r") as z:
                for target in ["word/document.xml", "word/footnotes.xml"]:
                    if target in z.namelist():
                        xml_root = ET.fromstring(z.read(target))
                        for p in xml_root.iter():
                            if p.tag.endswith("}p"):
                                runs = [t.text for t in p.iter() if t.tag.endswith("}t") and t.text]
                                if runs:
                                    text_chunks.append("".join(runs))
                parser_info = "Native DOCX XML Engine (Paragraphs & Tables)"
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


def parse_date_string(raw_str):
    s = raw_str.strip()

    # 1. Numeric DD.MM.YYYY or DD-MM-YYYY or DD/MM/YYYY
    m1 = re.match(r"^(\d{1,2})[\.\-\/](\d{1,2})[\.\-\/]((?:19|20)\d{2})$", s)
    if m1:
        d, m, y = int(m1.group(1)), int(m1.group(2)), int(m1.group(3))
        try:
            return datetime.date(y, m, d)
        except ValueError:
            return None

    # 2. Numeric ISO YYYY-MM-DD or YYYY/MM/DD
    m2 = re.match(r"^((?:19|20)\d{2})[\-\/](\d{1,2})[\-\/](\d{1,2})$", s)
    if m2:
        y, m, d = int(m2.group(1)), int(m2.group(2)), int(m2.group(3))
        try:
            return datetime.date(y, m, d)
        except ValueError:
            return None

    # 3. Written DD Month YYYY (e.g., 14th October, 2026 or 1 August 2026)
    m3 = re.match(
        r"^(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?([A-Za-z]+),?\s+((?:19|20)\d{2})$",
        s,
        flags=re.IGNORECASE,
    )
    if m3:
        d = int(m3.group(1))
        mon_name = m3.group(2).lower().rstrip(".")
        y = int(m3.group(3))
        m = MONTH_MAP.get(mon_name)
        if m:
            try:
                return datetime.date(y, m, d)
            except ValueError:
                return None

    # 4. Written Month DD, YYYY (e.g., October 14, 2026)
    m4 = re.match(
        r"^([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+((?:19|20)\d{2})$",
        s,
        flags=re.IGNORECASE,
    )
    if m4:
        mon_name = m4.group(1).lower().rstrip(".")
        d = int(m4.group(2))
        y = int(m4.group(3))
        m = MONTH_MAP.get(mon_name)
        if m:
            try:
                return datetime.date(y, m, d)
            except ValueError:
                return None

    return None


def classify_legal_milestone(event_text):
    lower = event_text.lower()
    if any(k in lower for k in ["fir", "crime no", "173 bnss", "154 crpc", "first information", "complaint"]):
        return "FIR / CRIMINAL COMPLAINT"
    if any(k in lower for k in ["arrest", "35(3)", "41a", "remand", "custody", "bail"]):
        return "ARREST / LIBERTY SAFEGUARD"
    if any(k in lower for k in ["agreement", "contract", "mou", "invoice", "purchase order", "executed", "deed"]):
        return "CONTRACT / TRANSACTION"
    if any(k in lower for k in ["notice", "demand", "138", "legal notice", "reply", "12a"]):
        return "STATUTORY / LEGAL NOTICE"
    if any(k in lower for k in ["impugned", "order", "decree", "judgment", "cognizance", "summons", "award"]):
        return "JUDICIAL / IMPUGNED ORDER"
    if any(k in lower for k in ["charge sheet", "final report", "193 bnss", "173 crpc"]):
        return "FINAL REPORT / CHARGE SHEET"
    return "CASE EVENT / RECORD"


def clean_sentence_for_table(sentence):
    cleaned = re.sub(r"^[\s\-\*\•\#\|]+", "", sentence)
    cleaned = re.sub(r"\|", " - ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if len(cleaned) > 260:
        cleaned = cleaned[:257].rsplit(" ", 1)[0] + "..."
    return cleaned


def extract_chronology_events(content):
    month_names = "|".join(MONTH_MAP.keys())
    combined_date_regex = re.compile(
        rf"\b("
        rf"\d{{1,2}}[\.\-\/]\d{{1,2}}[\.\-\/](?:19|20)\d{{2}}"
        rf"|(?:19|20)\d{{2}}[\-\/]\d{{1,2}}[\-\/]\d{{1,2}}"
        rf"|\d{{1,2}}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:{month_names})\.?,?\s+(?:19|20)\d{{2}}"
        rf"|(?:{month_names})\.?\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s+(?:19|20)\d{{2}}"
        rf")\b",
        flags=re.IGNORECASE,
    )

    # Split content into logical lines / sentences
    raw_segments = re.split(r"(?:\r?\n|(?<=[\.\;\:])\s+)", content)
    events = []
    seen_keys = set()

    for seg in raw_segments:
        seg_clean = clean_sentence_for_table(seg)
        if len(seg_clean) < 12:
            continue
        matches = combined_date_regex.findall(seg_clean)
        if not matches:
            continue
        for raw_dt in matches:
            dt_obj = parse_date_string(raw_dt)
            if not dt_obj:
                continue
            # Filter out statutory enactment dates when merely citing Act titles
            if dt_obj in (datetime.date(2023, 12, 25), datetime.date(2024, 7, 1)) and (
                "sanhita" in seg_clean.lower() or "adhiniyam" in seg_clean.lower()
            ):
                continue

            milestone = classify_legal_milestone(seg_clean)
            dedup_key = (dt_obj.isoformat(), seg_clean[:80].lower())
            if dedup_key not in seen_keys:
                seen_keys.add(dedup_key)
                events.append({
                    "date": dt_obj,
                    "date_formatted": dt_obj.strftime("%d.%m.%Y"),
                    "milestone": milestone,
                    "particulars": seg_clean,
                })

    events.sort(key=lambda x: x["date"])
    return events


def synthesize_synopsis_points(content, events, jurisdiction):
    lower = content.lower()
    issues = []

    if "318" in lower or "420" in lower or "commercial" in lower or "breach of contract" in lower:
        issues.append(
            "The dispute arises out of a purely civil/commercial transaction sought to be given a criminal colour without foundational mens rea at the inception of the transaction (*State of Haryana v. Bhajan Lal*, 1992 Supp (1) SCC 335)."
        )
    if "35(3)" in lower or "35 bnss" in lower or "41a" in lower or "arnesh kumar" in lower:
        issues.append(
            "Mandatory pre-arrest procedural safeguards under Section 35(3) of the Bharatiya Nagarik Suraksha Sanhita, 2023 (formerly Section 41A CrPC) and the binding checklist in *Arnesh Kumar v. State of Bihar*, (2014) 8 SCC 273 are directly attracted."
        )
    if "47 bnss" in lower or "grounds of arrest" in lower or "prabir purkayastha" in lower:
        issues.append(
            "Non-supply of written grounds of arrest violates Article 22(1) of the Constitution and Section 47 BNSS, 2023 (*Prabir Purkayastha v. State (NCT of Delhi)*, (2024) 8 SCC 254)."
        )
    if "63(4)" in lower or "65b" in lower or "electronic" in lower:
        issues.append(
            "Reliance on secondary electronic records without a mandatory certificate under Section 63(4) of the Bharatiya Sakshya Adhiniyam, 2023 is inadmissible under *Arjun Panditrao Khotkar v. Kailash Kushanrao Gorantyal*, (2020) 7 SCC 1."
        )
    if "arbitration" in lower or "12(5)" in lower or "perkins" in lower:
        issues.append(
            "The dispute resolution mechanism attracts Section 12(5) and the Seventh Schedule of the Arbitration and Conciliation Act, 1996 (*CORE v. ECI SPIC*, 2024 SCC OnLine SC 3219)."
        )

    if not issues:
        issues.append(
            f"The {JURISDICTION_HEADERS[jurisdiction]['party_a'].title()} approaches this Hon'ble Court seeking appropriate statutory relief on the basis of the documented sequence of events set out in the Chronological List of Dates below."
        )

    if events:
        span_days = (events[-1]["date"] - events[0]["date"]).days
        issues.append(
            f"The documented chronology spans **{len(events)} key dated milestones** from **{events[0]['date_formatted']}** to **{events[-1]['date_formatted']}** ({span_days} days total span)."
        )

    return issues


def generate_chronology_document(file_path, jurisdiction="crlp"):
    os.makedirs(CHRONOLOGY_OUT_DIR, exist_ok=True)

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
        print(f"[Auto-Selected Newest File in Directory] -> {file_path}")

    if not os.path.exists(file_path):
        print(f"\n[Error] File '{file_path}' not found.")
        recent = list_recent_downloads(5)
        if recent:
            print("\nRecent documents in your ~/Downloads folder:")
            for idx, r in enumerate(recent, 1):
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(r)).strftime("%Y-%m-%d %H:%M")
                print(f"  {idx}. {r}  (Modified: {mtime})")
            print("\nTip: Run `python3 sweety.py legal chronology --latest` to extract from #1 automatically.\n")
        return

    content, parser_info = extract_document_text(file_path)
    events = extract_chronology_events(content)
    synopsis_points = synthesize_synopsis_points(content, events, jurisdiction)
    hdr = JURISDICTION_HEADERS.get(jurisdiction, JURISDICTION_HEADERS["crlp"])
    today_filing = datetime.date.today().strftime("%d.%m.%Y")
    base_name = os.path.basename(file_path)

    print("\n=== SweetyAI High Court Synopsis & List of Dates Extractor ===")
    print(f"Source File     : {file_path}")
    print(f"Parser Engine   : {parser_info} ({len(content):,} chars)")
    print(f"Jurisdiction    : {hdr['court']} [{jurisdiction.upper()}]")
    print(f"Dated Events    : {len(events)} chronological milestones extracted")

    # Build Chronological Gap & Delay Audit Notes
    gap_alerts = []
    for i in range(1, len(events)):
        prev_ev = events[i - 1]
        curr_ev = events[i]
        delta = (curr_ev["date"] - prev_ev["date"]).days
        if delta > 90:
            gap_alerts.append(
                f"**{delta}-Day Interval ({prev_ev['date_formatted']} to {curr_ev['date_formatted']}):** "
                f"Between *{prev_ev['milestone']}* and *{curr_ev['milestone']}*. Verify whether delay requires explanation or attracts limitation/laches defense."
            )
        if "FIR" in curr_ev["milestone"] and delta >= 14:
            gap_alerts.append(
                f"**Unexplained Delay in FIR Registration ({delta} Days):** Between prior event on {prev_ev['date_formatted']} and FIR on {curr_ev['date_formatted']}. "
                f"Triggers mandatory preliminary inquiry / delay scrutiny under Section 173(3) BNSS, 2023 and *Lalita Kumari v. Govt. of U.P.*, (2014) 2 SCC 1."
            )

    md_doc = f"""# {hdr['court']}
## {hdr['case_no']}
{hdr['provision']}

**BETWEEN:**
[Name of the {hdr['party_a'].title()}] ... **{hdr['party_a']}**

**AND:**
[Name of the {hdr['party_b'].title()}] ... **{hdr['party_b']}**

---

## SYNOPSIS

The {hdr['party_a'].title()} respectfully submits this concise Synopsis and Chronological List of Dates and Events for the kind perusal of this Hon'ble Court:

"""
    for idx, pt in enumerate(synopsis_points, 1):
        md_doc += f"{idx}. {pt}\n"

    md_doc += """
---

## CHRONOLOGICAL LIST OF DATES AND EVENTS

| Sl. No. | Date (DD.MM.YYYY) | Stage / Milestone | Particulars of Events |
| :--- | :--- | :--- | :--- |
"""
    if events:
        for idx, ev in enumerate(events, 1):
            md_doc += f"| {idx}. | **{ev['date_formatted']}** | `{ev['milestone']}` | {ev['particulars']} |\n"
        next_sl = len(events) + 1
    else:
        md_doc += "| 1. | **[Date to be inserted]** | `FACTUAL MATRIX` | No explicit calendar dates detected in source text; insert transaction/FIR dates from annexures. |\n"
        next_sl = 2

    md_doc += f"| {next_sl}. | **{today_filing}** | `PRESENT FILING` | Hence, aggrieved by the aforesaid action/proceedings, the {hdr['party_a'].title()} is constrained to present this Memorandum before this Hon'ble Court. |\n"

    md_doc += "\n---\n\n## AUTOMATED PROCEDURAL DELAY & TIME-GAP AUDIT (FOR COUNSEL'S BRIEF)\n"
    if gap_alerts:
        for alert in gap_alerts:
            md_doc += f"- {alert}\n"
    else:
        md_doc += "- No abnormal inter-event time gaps (>90 days) or delayed FIR intervals detected across extracted dates.\n"

    md_doc += f"""
---
**BENGALURU**
**DATE: {today_filing}**

**ADVOCATE FOR THE {hdr['party_a']}**
"""

    slug = os.path.splitext(base_name)[0].replace(" ", "_")
    out_path = os.path.join(CHRONOLOGY_OUT_DIR, f"synopsis_list_of_dates_{slug}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md_doc)

    print("\n" + md_doc)
    print("=========================================================================")
    print(f"[Success] High Court Synopsis & List of Dates saved -> '{out_path}'")
    print(f"          (Run `python3 sweety.py export {out_path}` for A4 High Court HTML/PDF)")
    print("=========================================================================\n")


def handle_chronology_cli(argv):
    parser = argparse.ArgumentParser(
        prog="sweety legal chronology",
        description="Extract a High Court of Karnataka compliant Synopsis & Chronological List of Dates from PDF/DOCX/MD/TXT files.",
    )
    parser.add_argument("file", nargs="?", help="Path to case file, FIR, pleading, contract, or directory")
    parser.add_argument(
        "--jurisdiction",
        choices=["crlp", "wp", "rfa", "comm"],
        default="crlp",
        help="Filing format: crlp (Sec 528 BNSS), wp (Art 226/227), rfa (First Appeal), comm (Commercial Court)",
    )
    parser.add_argument("--latest", action="store_true", help="Automatically extract chronology from the newest file in ~/Downloads")
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
        generate_chronology_document(recent[0], args.jurisdiction)
    elif args.file:
        generate_chronology_document(args.file, args.jurisdiction)
    else:
        parser.print_help()


if __name__ == "__main__":
    handle_chronology_cli(sys.argv[1:])
