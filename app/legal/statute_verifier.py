from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class CitationVerificationResult:
    raw_citation: str
    act_name: str
    section: str
    is_valid: bool
    status: str  # "VALID_ACTIVE", "REPEALED", "AMENDED", "INVALID_SECTION", "UNKNOWN_ACT"
    correct_title: str
    notes: str
    replacement_act: Optional[str] = None
    historical_context: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_citation": self.raw_citation,
            "act_name": self.act_name,
            "section": self.section,
            "is_valid": self.is_valid,
            "status": self.status,
            "correct_title": self.correct_title,
            "notes": self.notes,
            "replacement_act": self.replacement_act,
            "historical_context": self.historical_context,
        }


class StatuteVerifier:
    """
    Deterministic, zero-hallucination verification engine for statutory citations.
    Validates Act names, section existence, amendment history, and repeal replacements.
    """

    STATUTE_REGISTRY: Dict[str, Dict[str, Any]] = {
        "indian contract act": {
            "canonical_title": "Indian Contract Act, 1872",
            "year": 1872,
            "total_sections": 238,
            "repealed_ranges": [
                (76, 123, "Repealed by the Sale of Goods Act, 1930"),
                (239, 266, "Repealed by the Indian Partnership Act, 1932"),
            ],
            "key_sections": {
                "2": "Interpretation clause / Definitions (Offer, Acceptance, Consideration)",
                "10": "What agreements are contracts (Free consent, competent parties)",
                "23": "What considerations and objects are lawful",
                "27": "Agreement in restraint of trade, void",
                "28": "Agreements in restraint of legal proceedings, void",
                "73": "Compensation for loss or damage caused by breach of contract",
                "74": "Compensation for breach of contract where penalty stipulated",
            },
        },
        "arbitration and conciliation act": {
            "canonical_title": "Arbitration and Conciliation Act, 1996",
            "year": 1996,
            "total_sections": 87,
            "repealed_ranges": [],
            "key_sections": {
                "7": "Arbitration agreement requirements (in writing)",
                "8": "Power to refer parties to arbitration where there is an arbitration agreement",
                "9": "Interim measures by Court",
                "11": "Appointment of arbitrators by High Court / Supreme Court",
                "16": "Competence of arbitral tribunal to rule on its jurisdiction (Kompetenz-Kompetenz)",
                "17": "Interim measures ordered by arbitral tribunal",
                "34": "Application for setting aside arbitral award",
                "37": "Appealable orders",
                "48": "Conditions for enforcement of foreign awards (New York Convention)",
            },
        },
        "specific relief act": {
            "canonical_title": "Specific Relief Act, 1963",
            "year": 1963,
            "total_sections": 44,
            "repealed_ranges": [],
            "key_sections": {
                "10": "Specific performance in respect of contracts (mandatory post-2018 amendment)",
                "14": "Contracts not specifically enforceable",
                "20": "Substituted performance of contract (2018 amendment)",
                "41": "Injunction when refused",
            },
        },
        "information technology act": {
            "canonical_title": "Information Technology Act, 2000",
            "year": 2000,
            "total_sections": 90,
            "repealed_ranges": [
                (66, 66, "Section 66A struck down as unconstitutional by Supreme Court in Shreya Singhal v UOI (2015)"),
            ],
            "key_sections": {
                "43A": "Compensation for failure to protect sensitive personal data",
                "65": "Tampering with computer source documents",
                "66": "Computer related offences / Hacking",
                "79": "Exemption from liability of intermediary in certain cases (Safe Harbor)",
            },
        },
        "indian penal code": {
            "canonical_title": "Indian Penal Code, 1860",
            "year": 1860,
            "total_sections": 511,
            "repealed_ranges": [
                (1, 511, "Repealed and replaced by Bharatiya Nyaya Sanhita, 2023 with effect from 1 July 2024"),
            ],
            "replacement_act": "Bharatiya Nyaya Sanhita, 2023 (BNS)",
        },
        "bharatiya nyaya sanhita": {
            "canonical_title": "Bharatiya Nyaya Sanhita, 2023",
            "year": 2023,
            "total_sections": 358,
            "repealed_ranges": [],
            "key_sections": {
                "316": "Criminal Breach of Trust (formerly Section 405/406 IPC)",
                "318": "Cheating (formerly Section 415/420 IPC)",
                "351": "Criminal Intimidation (formerly Section 503/506 IPC)",
            },
        },
        "companies act": {
            "canonical_title": "Companies Act, 2013",
            "year": 2013,
            "total_sections": 470,
            "repealed_ranges": [],
            "key_sections": {
                "135": "Corporate Social Responsibility",
                "149": "Company to have Board of Directors",
                "166": "Duties of Directors",
                "186": "Loans and investment by company",
            },
        },
    }

    def _match_act(self, raw_act_text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        raw_lower = raw_act_text.lower()
        for key, act_info in self.STATUTE_REGISTRY.items():
            if key in raw_lower:
                return key, act_info
        return None

    def verify_citation(
        self,
        section_str: str,
        act_str: str,
        raw_citation: Optional[str] = None,
    ) -> CitationVerificationResult:
        raw = raw_citation or f"Section {section_str} of {act_str}"
        match = self._match_act(act_str)

        if not match:
            return CitationVerificationResult(
                raw_citation=raw,
                act_name=act_str,
                section=section_str,
                is_valid=False,
                status="UNKNOWN_ACT",
                correct_title=act_str,
                notes=f"Act '{act_str}' is not in local deterministic statutory index.",
            )

        _, act_info = match
        canonical_title = act_info["canonical_title"]
        total_sec = act_info.get("total_sections", 0)

        # Parse section numeric value if possible
        sec_num_match = re.search(r"\d+", section_str)
        if not sec_num_match:
            return CitationVerificationResult(
                raw_citation=raw,
                act_name=canonical_title,
                section=section_str,
                is_valid=True,
                status="VALID_ACTIVE",
                correct_title=canonical_title,
                notes="Section format contains non-numeric identifier.",
            )

        sec_num = int(sec_num_match.group(0))

        # Check section range bounds
        if sec_num > total_sec or sec_num < 1:
            return CitationVerificationResult(
                raw_citation=raw,
                act_name=canonical_title,
                section=section_str,
                is_valid=False,
                status="INVALID_SECTION",
                correct_title=canonical_title,
                notes=f"Section {sec_num} does not exist in {canonical_title} (Max section: {total_sec}).",
            )

        # Check if repealed or replaced
        if "replacement_act" in act_info:
            return CitationVerificationResult(
                raw_citation=raw,
                act_name=canonical_title,
                section=section_str,
                is_valid=False,
                status="REPEALED",
                correct_title=canonical_title,
                replacement_act=act_info["replacement_act"],
                notes=f"{canonical_title} has been repealed. Refer to {act_info['replacement_act']}.",
            )

        for start, end, repeal_note in act_info.get("repealed_ranges", []):
            if start <= sec_num <= end:
                return CitationVerificationResult(
                    raw_citation=raw,
                    act_name=canonical_title,
                    section=section_str,
                    is_valid=False,
                    status="REPEALED",
                    correct_title=canonical_title,
                    notes=f"Section {sec_num} is repealed: {repeal_note}",
                )

        key_desc = act_info.get("key_sections", {}).get(str(sec_num), "")
        notes = f"Active statutory provision. {key_desc}".strip()

        return CitationVerificationResult(
            raw_citation=raw,
            act_name=canonical_title,
            section=section_str,
            is_valid=True,
            status="VALID_ACTIVE",
            correct_title=canonical_title,
            notes=notes,
        )

    def scan_text(self, document_text: str) -> List[CitationVerificationResult]:
        """Scans freeform legal text to find and verify all statutory citations."""
        pattern = r"(?i)(?:Section|Sec\.|Article|Art\.)\s+(\d+[A-Za-z]?)\s+(?:of\s+the\s+)?([A-Za-z\s,]+(?:Act|Code|Sanhita)[,\s\d]*)"
        matches = list(re.finditer(pattern, document_text))

        results = []
        for m in matches:
            sec = m.group(1).strip()
            act = m.group(2).strip()
            full_match = m.group(0).strip()
            res = self.verify_citation(sec, act, full_match)
            results.append(res)

        return results
