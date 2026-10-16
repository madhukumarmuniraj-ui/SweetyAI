from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.legal.playbook_engine import ClauseRule, PlaybookEngine
from app.sandbox.diff_verifier import DiffResult, DiffVerifier

logger = logging.getLogger(__name__)


@dataclass
class ClauseTriageResult:
    clause_id: str
    title: str
    category: Optional[str]
    category_name: str
    risk_tier: str  # "RED", "AMBER", "GREEN", "UNCLASSIFIED"
    issues: List[str]
    guidance: str
    original_text: str
    recommended_text: str
    diff: Optional[DiffResult] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clause_id": self.clause_id,
            "title": self.title,
            "category": self.category,
            "category_name": self.category_name,
            "risk_tier": self.risk_tier,
            "issues": self.issues,
            "guidance": self.guidance,
            "original_text": self.original_text,
            "recommended_text": self.recommended_text,
            "diff": self.diff.to_dict() if self.diff else None,
        }


@dataclass
class ContractTriageReport:
    total_clauses: int
    red_count: int
    amber_count: int
    green_count: int
    unclassified_count: int
    overall_risk_score: float  # 0 to 100
    risk_level: str  # "HIGH", "MODERATE", "LOW"
    clauses: List[ClauseTriageResult] = field(default_factory=list)
    executive_summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_clauses": self.total_clauses,
            "red_count": self.red_count,
            "amber_count": self.amber_count,
            "green_count": self.green_count,
            "unclassified_count": self.unclassified_count,
            "overall_risk_score": round(self.overall_risk_score, 1),
            "risk_level": self.risk_level,
            "executive_summary": self.executive_summary,
            "clauses": [c.to_dict() for c in self.clauses],
        }


class ClauseTriager:
    """
    Evaluates contract clauses against the legal playbook, computes risk tiers
    (Red/Amber/Green), identifies negotiation deviations, and generates redline replacement diffs.
    """

    def __init__(self, playbook_engine: Optional[PlaybookEngine] = None):
        self.engine = playbook_engine or PlaybookEngine()

    def triage_clause(
        self,
        clause_id: str,
        title: str,
        text: str,
    ) -> ClauseTriageResult:
        category = self.engine.classify_clause(text, title)
        if not category or category not in self.engine.rules:
            return ClauseTriageResult(
                clause_id=clause_id,
                title=title,
                category=None,
                category_name="General Clause",
                risk_tier="UNCLASSIFIED",
                issues=[],
                guidance="Standard operational clause outside prioritized playbook categories.",
                original_text=text,
                recommended_text=text,
                diff=None,
            )

        rule = self.engine.rules[category]
        text_lower = text.lower()
        issues: List[str] = []

        # 1. Check RED triggers
        red_found = []
        for trigger in rule.red_triggers:
            if trigger.lower() in text_lower:
                red_found.append(trigger)

        # 2. Check AMBER triggers
        amber_found = []
        for trigger in rule.amber_triggers:
            if trigger.lower() in text_lower:
                amber_found.append(trigger)

        # 3. Check GREEN triggers
        green_found = []
        for trigger in rule.green_triggers:
            if trigger.lower() in text_lower:
                green_found.append(trigger)

        # Determine Risk Tier
        if red_found:
            risk_tier = "RED"
            for rf in red_found:
                issues.append(f"Critical Deviation: Found '{rf}'. {rule.guidance}")
            recommended = rule.fallback_clause
        elif amber_found:
            risk_tier = "AMBER"
            for af in amber_found:
                issues.append(f"Moderate Risk: Detected '{af}'. Consider aligning with standard terms.")
            recommended = rule.fallback_clause
        elif green_found or len(text.strip()) > 30:
            risk_tier = "GREEN"
            issues.append("Compliant with enterprise playbook standards.")
            recommended = text
        else:
            risk_tier = "AMBER"
            issues.append("Ambiguous clause wording requiring legal review.")
            recommended = rule.fallback_clause

        diff = DiffVerifier.compute_diff(text, recommended, filename=f"{category}.txt") if recommended != text else None

        return ClauseTriageResult(
            clause_id=clause_id,
            title=title,
            category=category,
            category_name=rule.name,
            risk_tier=risk_tier,
            issues=issues,
            guidance=rule.guidance,
            original_text=text,
            recommended_text=recommended,
            diff=diff,
        )

    def triage_contract(self, contract_text: str) -> ContractTriageReport:
        """Splits full contract and generates a comprehensive Red/Amber/Green triage report."""
        raw_clauses = self.engine.split_into_clauses(contract_text)
        results: List[ClauseTriageResult] = []

        red_count = 0
        amber_count = 0
        green_count = 0
        unclassified_count = 0

        for item in raw_clauses:
            res = self.triage_clause(item["id"], item["title"], item["text"])
            results.append(res)
            if res.risk_tier == "RED":
                red_count += 1
            elif res.risk_tier == "AMBER":
                amber_count += 1
            elif res.risk_tier == "GREEN":
                green_count += 1
            else:
                unclassified_count += 1

        total = len(results)
        # Compute Weighted Risk Score (0-100)
        # Red weight: 100, Amber weight: 50, Green weight: 10
        if total > 0:
            weighted_points = (red_count * 100) + (amber_count * 50) + (green_count * 10)
            risk_score = min(100.0, weighted_points / total)
        else:
            risk_score = 0.0

        if risk_score >= 60.0 or red_count >= 2:
            risk_level = "HIGH"
        elif risk_score >= 30.0 or amber_count >= 2:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"

        exec_summary = (
            f"Contract Review Complete: Analyzed {total} clauses. "
            f"Found {red_count} Critical (RED), {amber_count} Moderate (AMBER), and {green_count} Compliant (GREEN) clauses. "
            f"Overall Risk Profile: {risk_level} ({round(risk_score, 1)}/100)."
        )

        return ContractTriageReport(
            total_clauses=total,
            red_count=red_count,
            amber_count=amber_count,
            green_count=green_count,
            unclassified_count=unclassified_count,
            overall_risk_score=risk_score,
            risk_level=risk_level,
            clauses=results,
            executive_summary=exec_summary,
        )
