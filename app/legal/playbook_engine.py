from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ClauseRule:
    category: str
    name: str
    keywords: List[str]
    standard_rule: str
    red_triggers: List[str]
    amber_triggers: List[str]
    green_triggers: List[str]
    fallback_clause: str
    guidance: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "name": self.name,
            "keywords": self.keywords,
            "standard_rule": self.standard_rule,
            "red_triggers": self.red_triggers,
            "amber_triggers": self.amber_triggers,
            "green_triggers": self.green_triggers,
            "fallback_clause": self.fallback_clause,
            "guidance": self.guidance,
        }


class PlaybookEngine:
    """
    Loads standard enterprise contract playbooks, splits legal documents into
    discrete clauses, and maps text against categorized policy criteria.
    """

    def __init__(self, playbook_path: Optional[str] = None):
        self.playbook_path = playbook_path or os.path.join(
            os.path.dirname(__file__), "legal_playbook.json"
        )
        self.rules: Dict[str, ClauseRule] = {}
        self.load_playbook(self.playbook_path)

    def load_playbook(self, filepath: str) -> bool:
        if not os.path.exists(filepath):
            logger.warning(f"[PlaybookEngine] Playbook file not found: {filepath}")
            return False
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            categories = data.get("categories", {})
            self.rules.clear()
            for cat_id, cat_data in categories.items():
                self.rules[cat_id] = ClauseRule(
                    category=cat_id,
                    name=cat_data.get("name", cat_id.replace("_", " ").title()),
                    keywords=cat_data.get("keywords", []),
                    standard_rule=cat_data.get("standard_rule", ""),
                    red_triggers=cat_data.get("red_triggers", []),
                    amber_triggers=cat_data.get("amber_triggers", []),
                    green_triggers=cat_data.get("green_triggers", []),
                    fallback_clause=cat_data.get("fallback_clause", ""),
                    guidance=cat_data.get("guidance", ""),
                )
            logger.info(f"[PlaybookEngine] Loaded {len(self.rules)} legal playbook rules from {filepath}")
            return True
        except Exception as e:
            logger.error(f"[PlaybookEngine] Error loading playbook: {e}")
            return False

    def split_into_clauses(self, contract_text: str) -> List[Dict[str, str]]:
        """
        Parses full contract text into structured clause units by section numbers and headings.
        """
        if not contract_text or not contract_text.strip():
            return []

        # Regex patterns for section numbers like:
        # "1. Limitation of Liability", "Section 2. Indemnity", "Article III: Term", "1.1 Confidentiality"
        pattern = r"(?m)^(?:(?:Section|Article|Clause)\s+)?(?:\d+|[IVXLCDM]+)(?:\.\d+)*[\.:\s]+[^\n]+"
        matches = list(re.finditer(pattern, contract_text))

        clauses: List[Dict[str, str]] = []

        if not matches:
            # Fall back to double newlines or paragraph blocks
            paragraphs = [p.strip() for p in contract_text.split("\n\n") if p.strip()]
            for idx, p in enumerate(paragraphs, 1):
                first_line = p.splitlines()[0][:60]
                clauses.append({
                    "id": f"clause_{idx}",
                    "title": first_line,
                    "text": p,
                })
            return clauses

        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(contract_text)
            heading = match.group(0).strip()
            body = contract_text[start:end].strip()

            clauses.append({
                "id": f"clause_{i + 1}",
                "title": heading,
                "text": body,
            })

        return clauses

    def classify_clause(self, clause_text: str, title: str = "") -> Optional[str]:
        """Identifies which playbook category a clause belongs to."""
        text_lower = f"{title} {clause_text}".lower()

        best_category = None
        highest_score = 0

        for cat_id, rule in self.rules.items():
            score = 0
            # Direct category name match
            if rule.name.lower() in text_lower:
                score += 5
            # Keyword matches
            for kw in rule.keywords:
                if kw.lower() in text_lower:
                    score += 2

            if score > highest_score:
                highest_score = score
                best_category = cat_id

        return best_category if highest_score >= 2 else None

    def get_rule(self, category: str) -> Optional[ClauseRule]:
        return self.rules.get(category)
