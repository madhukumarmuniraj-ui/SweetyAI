"""
SweetyAI Precedent & Statutory Citation Verifier Engine
Cross-references sections across IPC/BNS, CrPC/BNSS, Evidence Act/BSA, and NI Act.

Public API:
  - CitationVerifier.verify_citation(query)             -> single-query verdict string
  - extract_all_citations(text)                         -> (cases, reporters, statutes)
  - validate_statute_reference("Section 318(4) BNS")    -> (status, note)
  - verify_case_grounding("Arnesh Kumar v. State of Bihar") -> (status, note)
  - verify_file_citations(file_path)                    -> dict summary + audit report on disk
  - handle_verify_cli(args)                             -> CLI entry point
"""

import os
import re
import sys

STATUTORY_MAPPING = {
    "IPC_TO_BNS": {
        "Section 420 IPC": "Section 316 BNS (Cheating and dishonestly inducing delivery of property)",
        "Section 406 IPC": "Section 316(2) BNS (Criminal breach of trust)",
        "Section 302 IPC": "Section 103 BNS (Punishment for murder)",
        "Section 376 IPC": "Section 64 BNS (Rape)"
    },
    "CRPC_TO_BNSS": {
        "Section 154 CrPC": "Section 173 BNSS (Information in cognizable cases - FIR)",
        "Section 438 CrPC": "Section 482 BNSS (Direction for grant of bail to person apprehending arrest)",
        "Section 161 CrPC": "Section 180 BNSS (Examination of witnesses by police)"
    },
    "NI_ACT": {
        "Section 138 NI Act": "Dishonour of cheque for insufficiency, etc., of funds in the account.",
        "Section 142 NI Act": "Cognizance of offences."
    }
}

# Canonical act code -> (display name, total sections) for boundary checks
STATUTE_ALIASES = {
    "BNS": ("BNS", 358),
    "BHARATIYA NYAYA SANHITA": ("BNS", 358),
    "BNSS": ("BNSS", 531),
    "BHARATIYA NAGARIK SURAKSHA SANHITA": ("BNSS", 531),
    "BSA": ("BSA", 170),
    "BHARATIYA SAKSHYA ADHINIYAM": ("BSA", 170),
    "IPC": ("IPC", 511),
    "INDIAN PENAL CODE": ("IPC", 511),
    "CRPC": ("CrPC", 484),
    "CR.P.C": ("CrPC", 484),
    "CRIMINAL PROCEDURE CODE": ("CrPC", 484),
    "IEA": ("IEA", 167),
    "INDIAN EVIDENCE ACT": ("IEA", 167),
    "NI ACT": ("NI Act", 147),
    "NEGOTIABLE INSTRUMENTS ACT": ("NI Act", 147),
}

# Legacy (pre-2023 code) acts and their successor statutes under the new criminal codes
LEGACY_TO_NEW = {
    "IPC": ("BNS, 2023", "IPC_TO_BNS"),
    "CrPC": ("BNSS, 2023", "CRPC_TO_BNSS"),
    "IEA": ("BSA, 2023", None),
}

_SECTION_PATTERN = re.compile(
    r"\b(?:Section|Sec\.|S\.)\s*(\d+[A-Za-z]?(?:\(\d+\))?)\s+(?:of\s+)?(?:the\s+)?"
    r"((?:[A-Z][A-Za-z,.'-]*\s+){0,5}(?:Act|Sanhita|Adhiniyam|Code)(?:\s*,?\s*\d{4})?|BNS|BNSS|BSA|IPC|CrPC|IEA|NI Act)\b"
)

_NAME = r"[A-Z][A-Za-z0-9.'&\-]+"
_CASE_PATTERN = re.compile(
    rf"({_NAME}(?:\s+(?:of|the|and|&|{_NAME})){{0,7}})\s+v(?:s)?\.?\s+"
    rf"({_NAME}(?:\s+(?:of|the|and|&|{_NAME})){{0,7}})"
)

_REPORTER_PATTERN = re.compile(
    r"\b\d{4}\)?\s*[^\n]{0,14}?\b(SCC|SCR|Supp|Cr\.?\s?LJ|Kant\.?\s?LJ)\b[^\n]{0,10}?\d+"
)


def _dedupe(items):
    seen, out = set(), []
    for item in items:
        key = re.sub(r"\s+", " ", item.strip())
        if key and key not in seen:
            seen.add(key)
            out.append(key)
    return out


class CitationVerifier:
    def verify_citation(self, citation_query: str) -> str:
        query_upper = citation_query.upper()
        for category, mappings in STATUTORY_MAPPING.items():
            for old_sec, new_sec in mappings.items():
                if query_upper in old_sec.upper() or query_upper in new_sec.upper():
                    return f"[VERIFIED - {category}] Match Found: {old_sec} <---> {new_sec}"
        return f"[UNVERIFIED/CUSTOM CITATION]: '{citation_query}' requires manual bench precedent validation."


# -----------------------------------------------------------------------------
# FULL PIPELINE API (used by full_audit_pipeline.py and the audit CLI)
# -----------------------------------------------------------------------------

def extract_all_citations(text_content: str):
    """Extract (case_titles, reporter_citations, statutory_references) from text."""
    if not text_content:
        return [], [], []

    cases = []
    for prefix, suffix in _CASE_PATTERN.findall(text_content):
        cases.append(f"{prefix} v. {suffix}")

    reporters = [m.group(0) for m in _REPORTER_PATTERN.finditer(text_content)]

    statutes = []
    for section, act in _SECTION_PATTERN.findall(text_content):
        statutes.append(f"Section {section} of {act.strip().rstrip(',')}")

    return _dedupe(cases), _dedupe(reporters), _dedupe(statutes)


def _match_alias(ref_upper: str):
    """Longest-word-boundary alias match against the local statute index."""
    best = None
    for alias, info in STATUTE_ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", ref_upper) and (best is None or len(alias) > len(best[0])):
            best = (alias, info)
    return best


def validate_statute_reference(statute_ref: str):
    """Return (status, note) for a 'Section X of ACT' style citation string.

    status is one of: VERIFIED, WARNING (legacy code), CRITICAL (out of range), UNVERIFIED.
    """
    ref_upper = re.sub(r"\s+", " ", str(statute_ref).strip().upper())

    sec_match = re.search(r"(?:SECTION|SEC\.?|S\.)\s*(\d+[A-Z]?(?:\(\d+\))?)", ref_upper)
    sec = sec_match.group(1) if sec_match else None

    alias_match = _match_alias(ref_upper)
    if alias_match is None:
        return ("UNVERIFIED", "Act not present in the local statutory index; manual bench verification required.")

    _, (act, total) = alias_match

    if sec is None:
        return ("UNVERIFIED", f"Could not parse a section number from '{statute_ref}'.")

    base = int(re.match(r"\d+", sec).group(0))

    if base < 1 or base > total:
        return ("CRITICAL", f"Section {sec} exceeds the statutory range of the {act} (1-{total}). Possible hallucinated citation.")

    if act in LEGACY_TO_NEW:
        new_code, mapping_key = LEGACY_TO_NEW[act]
        replacement = None
        if mapping_key:
            for old_sec, new_sec in STATUTORY_MAPPING.get(mapping_key, {}).items():
                if sec in old_sec:
                    replacement = new_sec
                    break
        replacement = replacement or f"the corresponding provision of the {new_code}"
        return ("WARNING", f"Legacy pre-2023 citation ({act}): re-verify and plead as {replacement}.")

    if act == "NI Act" and base == 138:
        return ("VERIFIED", STATUTORY_MAPPING["NI_ACT"]["Section 138 NI Act"])

    return ("VERIFIED", f"Section {sec} of the {act} is within the statutory range (1-{total}).")


def verify_case_grounding(case_citation: str):
    """Return (status, note) assessing the citation grounding of a case title."""
    text = str(case_citation)
    has_year = bool(re.search(r"\b(?:19|20)\d{2}\b", text))
    has_reporter = bool(re.search(r"\b(SCC|SCR|AIR|Supp|Cr\.?\s?LJ|Kant\.?\s?LJ)\b", text))

    if has_year and has_reporter:
        return ("GROUNDED", "Reporter citation detected alongside the case title.")
    if has_year:
        return ("PARTIALLY_GROUNDED", "Year present; reporter/neutral citation not detected in the title.")
    return ("NEEDS_SUPPORT", "No year or reporter citation attached; attach the certified copy before filing.")


def _read_text_for_audit(file_path: str) -> str:
    """Read plain-text/markdown directly; for binary formats use the privacy engine extractor."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in (".txt", ".md", ".markdown", ".csv", ".json"):
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    try:
        from privacy_and_playbook_engine import extract_text_and_metadata
        text_content, _metadata = extract_text_and_metadata(file_path)
        return text_content or ""
    except Exception as e:
        return f"[Extraction warning] Could not extract text from {file_path}: {e}"


def verify_file_citations(file_path: str):
    """Run the full citation audit over a file, print a summary and save a markdown report."""
    text_content = _read_text_for_audit(file_path)

    cases, reporters, statutes = extract_all_citations(text_content)
    validated = [(s, *validate_statute_reference(s)) for s in statutes]
    alerts = [v for v in validated if v[1] in ("CRITICAL", "WARNING")]

    os.makedirs("citation_audit_reports", exist_ok=True)
    stem = os.path.splitext(os.path.basename(file_path))[0]
    out_path = f"citation_audit_reports/citation_audit_{stem}.md"

    lines = [
        "# SWEETYAI CITATION VERIFICATION AUDIT",
        f"**Source file:** `{file_path}`",
        "",
        f"- Case titles detected: **{len(cases)}**",
        f"- Reporter citations detected: **{len(reporters)}**",
        f"- Statutory references detected: **{len(statutes)}**",
        f"- Alerts (legacy code / out-of-range): **{len(alerts)}**",
        "",
        "## Statutory Boundary Checks",
    ]
    if validated:
        for stat, status, note in validated:
            lines.append(f"- **{stat}** — `{status}`: {note}")
    else:
        lines.append("- No statutory references detected.")

    lines.append("")
    lines.append("## Case Titles")
    if cases:
        for idx, case in enumerate(cases, 1):
            status, note = verify_case_grounding(case)
            lines.append(f"{idx}. **{case}** — `{status}` ({note})")
    else:
        lines.append("- No party-versus-party case titles detected.")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"[CitationVerifier] Cases: {len(cases)} | Reporters: {len(reporters)} | Statutes: {len(statutes)} | Alerts: {len(alerts)}")
    print(f"[CitationVerifier] Saved report to {out_path}")

    return {
        "cases": cases,
        "reporters": reporters,
        "statutes": statutes,
        "validations": validated,
        "alerts": alerts,
        "report_path": out_path,
    }


def handle_verify_cli(args):
    """CLI entry: verify a document file (if the argument is a path) or a citation query."""
    if args and len(args) >= 1 and os.path.exists(args[0]):
        verify_file_citations(args[0])
        return

    verifier = CitationVerifier()
    target = " ".join(args) if args else "Section 316 BNS"
    result = verifier.verify_citation(target)
    print(result)

    os.makedirs("citation_audit_reports", exist_ok=True)
    out_path = "citation_audit_reports/citation_audit_sample_contract.md"
    with open(out_path, "w") as out:
        out.write(f"# Citation Verification Audit\n\nQuery: {target}\n\nResult:\n{result}\n")
    print(f"[CitationVerifier] Saved report to {out_path}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        handle_verify_cli(sys.argv[1:])
    else:
        verifier = CitationVerifier()
        print(verifier.verify_citation("Section 420 IPC"))
        print(verifier.verify_citation("Section 154 CrPC"))
        print(verifier.verify_citation("Section 138 NI Act"))
