import os
import sys
import re
import json
import zipfile
import difflib
import datetime
import argparse
from xml.sax.saxutils import escape

DOCX_OUT_DIR = "word_docx_exports"
XLSX_OUT_DIR = "excel_claim_schedules"
MCP_OUT_FILE = "sweety_mcp_tools.json"


# ==============================================================================
# 1. ANTHROPIC SKILLS/DOCX ENGINE: NATIVE WORD .DOCX WITH TRACK CHANGES & KHC A4
# ==============================================================================
def _build_docx_zip(output_path, body_xml):
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default ContentType="application/vnd.openxmlformats-package.relationships+xml" Extension="rels"/>
  <Default ContentType="application/xml" Extension="xml"/>
  <Override ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml" PartName="/word/document.xml"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Target="word/document.xml" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"/>
</Relationships>"""

    # Karnataka High Court Ch. XII Rule 2 A4 Page Spec in Twips (1 inch = 1440 twips):
    # A4 = 11906 x 16838 twips | Left = 1.75 in (2520) | Right = 1.0 in (1440) | Top/Bottom = 1.5 in (2160)
    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
{body_xml}
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="2160" w:right="1440" w:bottom="2160" w:left="2520" w:header="720" w:footer="720" w:gutter="0"/>
    </w:sectPr>
  </w:body>
</w:document>"""

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", document_xml)


def export_markdown_to_khc_docx(md_path):
    os.makedirs(DOCX_OUT_DIR, exist_ok=True)
    if not os.path.exists(md_path):
        print(f"[Error] Source file '{md_path}' not found.")
        return

    with open(md_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()

    paragraphs_xml = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped == "---":
            continue

        is_h1 = stripped.startswith("# ")
        is_h2 = stripped.startswith("## ")
        is_h3 = stripped.startswith("### ")
        clean_text = re.sub(r"^#+\s*", "", stripped)
        clean_text = re.sub(r"\*\*(.*?)\*\*", r"\1", clean_text)
        clean_text = re.sub(r"`(.*?)`", r"\1", clean_text)
        esc_text = escape(clean_text)

        if is_h1 or is_h2:
            # Verdana 14pt (w:val="28" half-points), Bold, Centered, Single spacing
            p_xml = f"""    <w:p>
      <w:pPr>
        <w:jc w:val="center"/>
        <w:spacing w:before="240" w:after="120" w:line="240" w:lineRule="auto"/>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:rFonts w:ascii="Verdana" w:hAnsi="Verdana" w:cs="Verdana"/>
          <w:b/>
          <w:sz w:val="28"/>
        </w:rPr>
        <w:t>{esc_text}</w:t>
      </w:r>
    </w:p>"""
        elif is_h3:
            p_xml = f"""    <w:p>
      <w:pPr>
        <w:spacing w:before="180" w:after="80" w:line="360" w:lineRule="auto"/>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:rFonts w:ascii="Verdana" w:hAnsi="Verdana" w:cs="Verdana"/>
          <w:b/>
          <w:sz w:val="24"/>
        </w:rPr>
        <w:t>{esc_text}</w:t>
      </w:r>
    </w:p>"""
        else:
            # Verdana 12pt (w:val="24" half-points), Double spacing (w:line="480"), Justified
            p_xml = f"""    <w:p>
      <w:pPr>
        <w:jc w:val="both"/>
        <w:spacing w:before="60" w:after="120" w:line="480" w:lineRule="auto"/>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:rFonts w:ascii="Verdana" w:hAnsi="Verdana" w:cs="Verdana"/>
          <w:sz w:val="24"/>
        </w:rPr>
        <w:t>{esc_text}</w:t>
      </w:r>
    </w:p>"""
        paragraphs_xml.append(p_xml)

    base = os.path.splitext(os.path.basename(md_path))[0]
    out_docx = os.path.join(DOCX_OUT_DIR, f"{base}_khc_filing.docx")
    _build_docx_zip(out_docx, "\n".join(paragraphs_xml))
    print(f"[Success] Native Word .DOCX (KHC Ch. XII Rule 2 A4 Spec) generated -> '{out_docx}'")
    return out_docx


def generate_track_changes_docx(orig_path, mod_path, author="Madhukumar Muniraj (Advocate)"):
    os.makedirs(DOCX_OUT_DIR, exist_ok=True)
    if not os.path.exists(orig_path) or not os.path.exists(mod_path):
        print("[Error] Both original and modified files must exist.")
        return

    with open(orig_path, "r", encoding="utf-8", errors="replace") as f1:
        words1 = f1.read().split()
    with open(mod_path, "r", encoding="utf-8", errors="replace") as f2:
        words2 = f2.read().split()

    iso_now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    matcher = difflib.SequenceMatcher(None, words1, words2)
    runs_xml = []
    rev_id = 1

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            chunk = escape(" ".join(words1[i1:i2]) + " ")
            runs_xml.append(
                f'<w:r><w:rPr><w:rFonts w:ascii="Verdana" w:hAnsi="Verdana"/><w:sz w:val="24"/></w:rPr>'
                f'<w:t xml:space="preserve">{chunk}</w:t></w:r>'
            )
        elif tag in ("delete", "replace"):
            del_chunk = escape(" ".join(words1[i1:i2]) + " ")
            runs_xml.append(
                f'<w:del w:id="{rev_id}" w:author="{escape(author)}" w:date="{iso_now}">'
                f'<w:r><w:rPr><w:rFonts w:ascii="Verdana" w:hAnsi="Verdana"/><w:sz w:val="24"/></w:rPr>'
                f'<w:delText xml:space="preserve">{del_chunk}</w:delText></w:r></w:del>'
            )
            rev_id += 1
            if tag == "replace":
                ins_chunk = escape(" ".join(words2[j1:j2]) + " ")
                runs_xml.append(
                    f'<w:ins w:id="{rev_id}" w:author="{escape(author)}" w:date="{iso_now}">'
                    f'<w:r><w:rPr><w:rFonts w:ascii="Verdana" w:hAnsi="Verdana"/><w:sz w:val="24"/></w:rPr>'
                    f'<w:t xml:space="preserve">{ins_chunk}</w:t></w:r></w:ins>'
                )
                rev_id += 1
        elif tag == "insert":
            ins_chunk = escape(" ".join(words2[j1:j2]) + " ")
            runs_xml.append(
                f'<w:ins w:id="{rev_id}" w:author="{escape(author)}" w:date="{iso_now}">'
                f'<w:r><w:rPr><w:rFonts w:ascii="Verdana" w:hAnsi="Verdana"/><w:sz w:val="24"/></w:rPr>'
                f'<w:t xml:space="preserve">{ins_chunk}</w:t></w:r></w:ins>'
            )
            rev_id += 1

    header_p = """    <w:p>
      <w:pPr><w:jc w:val="center"/></w:pPr>
      <w:r><w:rPr><w:rFonts w:ascii="Verdana" w:hAnsi="Verdana"/><w:b/><w:sz w:val="28"/></w:rPr>
      <w:t>SWEETYAI NATIVE WORD TRACK-CHANGES REDLINE</w:t></w:r>
    </w:p>"""

    body_p = f"""    <w:p>
      <w:pPr><w:jc w:val="both"/><w:spacing w:line="480" w:lineRule="auto"/></w:pPr>
      {"".join(runs_xml)}
    </w:p>"""

    b1 = os.path.splitext(os.path.basename(orig_path))[0]
    b2 = os.path.splitext(os.path.basename(mod_path))[0]
    out_docx = os.path.join(DOCX_OUT_DIR, f"track_changes_{b1}_vs_{b2}.docx")
    _build_docx_zip(out_docx, header_p + "\n" + body_p)
    print(f"[Success] Native Word Track-Changes .DOCX (<w:ins>/<w:del>) saved -> '{out_docx}'")
    return out_docx


# ==============================================================================
# 2. ANTHROPIC SKILLS/XLSX ENGINE: FORMULA-DRIVEN COMMERCIAL CLAIM SCHEDULE
# ==============================================================================
def generate_commercial_interest_xlsx(principal, rate_pct, start_date_str, end_date_str=None, regime="sec34_cpc"):
    os.makedirs(XLSX_OUT_DIR, exist_ok=True)
    start_dt = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_dt = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else datetime.date.today()
    days = max(0, (end_dt - start_dt).days)
    interest_amt = principal * (rate_pct / 100.0) * (days / 365.0)
    total_claim = principal + interest_amt

    regime_labels = {
        "sec34_cpc": "Section 34 CPC, 1908 (Pre-Suit & Pendente Lite Commercial Interest)",
        "ni138_sec80": "Section 80 Negotiable Instruments Act, 1881 (Statutory 18% p.a. Dishonour Interest)",
        "msmed_sec16": "Section 16 MSMED Act, 2006 (3x RBI Bank Rate Compound Interest)",
        "arb_sec31_7": "Section 31(7)(a) & (b) Arbitration & Conciliation Act, 1996 (Pre-Award & Post-Award Interest)",
    }
    regime_desc = regime_labels.get(regime, regime_labels["sec34_cpc"])

    # Build native OpenXML .xlsx with live Excel formulas (=B5*(B6/100)*(B9/365) and =SUM(B5,B10))
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default ContentType="application/vnd.openxmlformats-package.relationships+xml" Extension="rels"/>
  <Default ContentType="application/xml" Extension="xml"/>
  <Override ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml" PartName="/xl/workbook.xml"/>
  <Override ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml" PartName="/xl/worksheets/sheet1.xml"/>
</Types>"""

    root_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Target="xl/workbook.xml" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"/>
</Relationships>"""

    wb_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets><sheet name="Claim_Interest_Schedule" sheetId="1" r:id="rId1"/></sheets>
</workbook>"""

    wb_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Target="worksheets/sheet1.xml" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"/>
</Relationships>"""

    sheet_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>
    <row r="1"><c r="A1" t="inlineStr"><is><t>SWEETYAI COMMERCIAL COURT &amp; ARBITRATION CLAIM SCHEDULE</t></is></c></row>
    <row r="2"><c r="A2" t="inlineStr"><is><t>Governing Statutory Regime</t></is></c><c r="B2" t="inlineStr"><is><t>{escape(regime_desc)}</t></is></c></row>
    <row r="4"><c r="A4" t="inlineStr"><is><t>Particulars</t></is></c><c r="B4" t="inlineStr"><is><t>Value / Formula</t></is></c></row>
    <row r="5"><c r="A5" t="inlineStr"><is><t>Principal Debt / Claim Amount (INR)</t></is></c><c r="B5"><v>{principal:.2f}</v></c></row>
    <row r="6"><c r="A6" t="inlineStr"><is><t>Annual Rate of Interest (% p.a.)</t></is></c><c r="B6"><v>{rate_pct:.2f}</v></c></row>
    <row r="7"><c r="A7" t="inlineStr"><is><t>Default / Accrual Start Date</t></is></c><c r="B7" t="inlineStr"><is><t>{start_dt.strftime('%d.%m.%Y')}</t></is></c></row>
    <row r="8"><c r="A8" t="inlineStr"><is><t>Computation End Date (Filing Date)</t></is></c><c r="B8" t="inlineStr"><is><t>{end_dt.strftime('%d.%m.%Y')}</t></is></c></row>
    <row r="9"><c r="A9" t="inlineStr"><is><t>Total Elapsed Days of Default</t></is></c><c r="B9"><v>{days}</v></c></row>
    <row r="10"><c r="A10" t="inlineStr"><is><t>Accrued Interest Amount (INR) [Live Formula]</t></is></c><c r="B10"><f>ROUND(B5*(B6/100)*(B9/365),2)</f><v>{interest_amt:.2f}</v></c></row>
    <row r="11"><c r="A11" t="inlineStr"><is><t>TOTAL SPECIFIED VALUE / CLAIM (INR) [Live Formula]</t></is></c><c r="B11"><f>SUM(B5,B10)</f><v>{total_claim:.2f}</v></c></row>
  </sheetData>
</worksheet>"""

    xlsx_path = os.path.join(XLSX_OUT_DIR, f"claim_schedule_{regime}_{int(principal)}.xlsx")
    with zipfile.ZipFile(xlsx_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", root_rels)
        zf.writestr("xl/workbook.xml", wb_xml)
        zf.writestr("xl/_rels/workbook.xml.rels", wb_rels)
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)

    md_path = os.path.join(XLSX_OUT_DIR, f"claim_schedule_{regime}_{int(principal)}.md")
    md_summary = f"""# COMMERCIAL SUIT / ARBITRATION INTEREST & SPECIFIED VALUE SCHEDULE
*(Prepared under Order VII Rule 2A CPC as amended by the Commercial Courts Act, 2015)*

| Sl. No. | Head of Claim | Statutory Basis / Formula | Computed Amount |
| :--- | :--- | :--- | :--- |
| 1. | **Principal Claim Amount** | Invoice / Contract / Cheque Principal | **INR {principal:,.2f}** |
| 2. | **Governing Interest Regime** | {regime_desc} | **{rate_pct:.2f}% per annum** |
| 3. | **Period of Default** | **{start_dt.strftime('%d.%m.%Y')}** to **{end_dt.strftime('%d.%m.%Y')}** | **{days} Days** |
| 4. | **Pre-Suit Interest Accrued** | `=ROUND(B5*(B6/100)*(B9/365), 2)` | **INR {interest_amt:,.2f}** |
| 5. | **TOTAL SPECIFIED VALUE (Sec. 12 CCA)** | `=SUM(B5, B10)` | **INR {total_claim:,.2f}** |
"""
    with open(md_path, "w", encoding="utf-8") as mf:
        mf.write(md_summary)

    print(md_summary)
    print(f"[Success] Live Formula-Driven Excel (.XLSX) saved -> '{xlsx_path}'")
    print(f"[Success] Order VII Rule 2A CPC Schedule (.MD) saved -> '{md_path}'")
    return xlsx_path


# ==============================================================================
# 3. ANTHROPIC MCP / TOOL-USE JSON SCHEMA REGISTRY FOR LOCAL LLM AGENTS
# ==============================================================================
def build_mcp_tool_registry():
    tools = [
        {
            "name": "sweety_full_case_audit",
            "description": "Runs the 6-stage Master Case Packet Pipeline (Privacy/BSA Sec 132, 6-Pillar Indian Contract Playbook, Citation/BNS/BNSS Verifier, High Court Synopsis & Chronology, Sec 63(4) BSA SHA-256 Certificate, and A4 Export).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Path to PDF, DOCX, MD, or TXT file"},
                    "jurisdiction": {"type": "string", "enum": ["crlp", "wp", "rfa", "comm"]},
                },
                "required": ["file"],
            },
        },
        {
            "name": "sweety_docx_track_changes",
            "description": "Generates a native Microsoft Word .docx file with real OpenXML Track Changes (<w:ins> and <w:del>) and Karnataka High Court A4 margins.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "original_file": {"type": "string"},
                    "modified_file": {"type": "string"},
                },
                "required": ["original_file", "modified_file"],
            },
        },
        {
            "name": "sweety_xlsx_claim_schedule",
            "description": "Generates a formula-driven Excel .xlsx Commercial Suit / Arbitration / NI Act interest calculation sheet under Order VII Rule 2A CPC.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "principal": {"type": "number"},
                    "rate": {"type": "number"},
                    "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "regime": {"type": "string", "enum": ["sec34_cpc", "ni138_sec80", "msmed_sec16", "arb_sec31_7"]},
                },
                "required": ["principal", "rate", "start_date"],
            },
        },
    ]
    with open(MCP_OUT_FILE, "w", encoding="utf-8") as f:
        json.dump({"mcp_version": "2026.1", "server_name": "sweetyai-indian-legal-suite", "tools": tools}, f, indent=2)
    print(f"[Success] Anthropic MCP Tool Schema Registry saved -> '{MCP_OUT_FILE}' ({len(tools)} agent tools registered)")


def handle_boost_cli(cmd, argv):
    if cmd == "docx-export":
        p = argparse.ArgumentParser(prog="sweety legal docx-export")
        p.add_argument("file", help="Markdown file to convert to Karnataka High Court A4 .docx")
        a = p.parse_args(argv)
        export_markdown_to_khc_docx(a.file)
    elif cmd == "docx-redline":
        p = argparse.ArgumentParser(prog="sweety legal docx-redline")
        p.add_argument("original", help="Original contract/pleading file")
        p.add_argument("modified", help="Modified contract/pleading file")
        p.add_argument("--author", default="Madhukumar Muniraj (Advocate)")
        a = p.parse_args(argv)
        generate_track_changes_docx(a.original, a.modified, a.author)
    elif cmd == "claim-xlsx":
        p = argparse.ArgumentParser(prog="sweety legal claim-xlsx")
        p.add_argument("--principal", type=float, required=True)
        p.add_argument("--rate", type=float, default=18.0)
        p.add_argument("--start-date", required=True, help="YYYY-MM-DD")
        p.add_argument("--end-date", default=None, help="YYYY-MM-DD")
        p.add_argument("--regime", choices=["sec34_cpc", "ni138_sec80", "msmed_sec16", "arb_sec31_7"], default="sec34_cpc")
        a = p.parse_args(argv)
        generate_commercial_interest_xlsx(a.principal, a.rate, a.start_date, a.end_date, a.regime)
    elif cmd == "mcp-sync":
        build_mcp_tool_registry()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        handle_boost_cli(sys.argv[1], sys.argv[2:])
    else:
        build_mcp_tool_registry()
