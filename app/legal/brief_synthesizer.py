from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.graph.knowledge_graph import KnowledgeGraph, get_knowledge_graph
from app.legal.clause_triager import ClauseTriager, ContractTriageReport
from app.legal.statute_verifier import CitationVerificationResult, StatuteVerifier

logger = logging.getLogger(__name__)


@dataclass
class ActionItem:
    action: str
    deadline_description: str
    urgency: str  # "CRITICAL", "HIGH", "MEDIUM", "ROUTINE"
    statutory_limitation: Optional[str] = None
    target_date: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "deadline_description": self.deadline_description,
            "urgency": self.urgency,
            "statutory_limitation": self.statutory_limitation,
            "target_date": self.target_date,
        }


@dataclass
class LegalBrief:
    title: str
    court_forum: str
    jurisdiction: str
    executive_summary: str
    questions_of_law: List[str]
    statutory_provisions: List[CitationVerificationResult]
    governing_precedents: List[Dict[str, Any]]
    clause_triage: Optional[ContractTriageReport]
    action_items: List[ActionItem]
    formatted_markdown: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "court_forum": self.court_forum,
            "jurisdiction": self.jurisdiction,
            "executive_summary": self.executive_summary,
            "questions_of_law": self.questions_of_law,
            "statutory_provisions": [s.to_dict() for s in self.statutory_provisions],
            "governing_precedents": self.governing_precedents,
            "clause_triage": self.clause_triage.to_dict() if self.clause_triage else None,
            "action_items": [a.to_dict() for a in self.action_items],
            "formatted_markdown": self.formatted_markdown,
        }


class BriefSynthesizer:
    """
    Synthesizes structured legal briefs, extracts questions of law,
    verifies statutory grounds, performs clause triage, and calculates limitation deadlines.
    """

    def __init__(
        self,
        statute_verifier: Optional[StatuteVerifier] = None,
        clause_triager: Optional[ClauseTriager] = None,
        knowledge_graph: Optional[KnowledgeGraph] = None,
    ):
        self.verifier = statute_verifier or StatuteVerifier()
        self.triager = clause_triager or ClauseTriager()
        self.graph = knowledge_graph or get_knowledge_graph()

    def _extract_questions_of_law(self, text: str) -> List[str]:
        """Identifies legal questions, disputed claims, and statutory interpretations."""
        questions = []
        pattern = r"(?i)(?:whether|issue|question)\s+[:\d\.\s]*([^\?\n]+\?)"
        for m in re.finditer(pattern, text):
            q_clean = m.group(0).strip()
            if len(q_clean) > 20 and q_clean not in questions:
                questions.append(q_clean)

        if not questions:
            # Generate representative questions based on content keywords
            text_lower = text.lower()
            if "breach" in text_lower or "damages" in text_lower:
                questions.append("Whether the alleged breach of contract entitles the claimant to unliquidated or liquidated damages under Section 73/74 ICA?")
            if "arbitration" in text_lower or "clause" in text_lower:
                questions.append("Whether the dispute falls within the substantive scope of the arbitration agreement under Section 7 of the Act?")
            if "non-compete" in text_lower or "restraint" in text_lower:
                questions.append("Whether the restrictive covenant is enforceable or void under Section 27 of the Indian Contract Act 1872?")

        return questions

    def _extract_action_items(self, text: str) -> List[ActionItem]:
        """Calculates limitation deadlines and immediate legal procedural milestones."""
        items: List[ActionItem] = []
        today = datetime.now()

        text_lower = text.lower()

        if "arbitral award" in text_lower or "section 34" in text_lower:
            limitation_date = (today + timedelta(days=90)).strftime("%Y-%m-%d")
            items.append(
                ActionItem(
                    action="File Section 34 Petition to set aside Arbitral Award",
                    deadline_description="Strict 90-day statutory limitation from receipt of signed award (extendable by 30 days on sufficient cause).",
                    urgency="CRITICAL",
                    statutory_limitation="Section 34(3), Arbitration and Conciliation Act 1996",
                    target_date=limitation_date,
                )
            )

        if "notice of dispute" in text_lower or "cure period" in text_lower:
            cure_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")
            items.append(
                ActionItem(
                    action="Issue Formal Written Notice of Dispute & Cure Demand",
                    deadline_description="30-day cure window prior to initiating formal termination or arbitration proceedings.",
                    urgency="HIGH",
                    target_date=cure_date,
                )
            )

        if "interim relief" in text_lower or "injunction" in text_lower:
            items.append(
                ActionItem(
                    action="File Urgent Section 9 / Order XXXIX Application for Interim Injunction",
                    deadline_description="Immediate filing required to preserve status quo and prevent asset dissipation.",
                    urgency="CRITICAL",
                    statutory_limitation="Section 9 Arbitration Act / CPC Order 39",
                )
            )

        if not items:
            items.append(
                ActionItem(
                    action="Issue Reply to Legal Notice / Demand Letter",
                    deadline_description="Standard 15-day response timeline to place factual defenses on record.",
                    urgency="HIGH",
                    target_date=(today + timedelta(days=15)).strftime("%Y-%m-%d"),
                )
            )

        return items

    def synthesize_brief(
        self,
        title: str,
        document_text: str,
        court_forum: str = "High Court / Arbitral Tribunal",
        jurisdiction: str = "India",
    ) -> LegalBrief:
        # 1. Scan and verify statutes
        statutes = self.verifier.scan_text(document_text)

        # 2. Triage contract clauses if present
        clause_triage = self.triager.triage_contract(document_text)

        # 3. Extract questions of law
        questions = self._extract_questions_of_law(document_text)

        # 4. Search graph for governing precedents
        precedents: List[Dict[str, Any]] = []
        for s in statutes:
            found_precedents = self.graph.find_precedents_for_statute(s.act_name)
            precedents.extend(found_precedents)

        # 5. Extract action items and limitation deadlines
        action_items = self._extract_action_items(document_text)

        # 6. Executive Summary
        exec_summary = (
            f"Legal Brief and Analysis for '{title}'. Forum: {court_forum}, Jurisdiction: {jurisdiction}. "
            f"Identified {len(statutes)} statutory citations ({sum(1 for s in statutes if s.is_valid)} verified active) "
            f"and {len(action_items)} procedural action items."
        )

        # 7. Formatted Markdown Synthesis
        md_lines = [
            f"# LEGAL BRIEF: {title.upper()}",
            f"**Forum / Court:** {court_forum} | **Jurisdiction:** {jurisdiction} | **Date:** {datetime.now().strftime('%d %B %Y')}",
            "---",
            "## 1. Executive Summary",
            exec_summary,
            "",
            "## 2. Core Questions of Law & Issues",
        ]
        for i, q in enumerate(questions, 1):
            md_lines.append(f"{i}. {q}")

        md_lines.append("")
        md_lines.append("## 3. Statutory Provisions & Grounding (Zero-Hallucination Verified)")
        if statutes:
            for s in statutes:
                status_tag = " [VERIFIED ACTIVE]" if s.is_valid else f" [WARNING: {s.status}]"
                md_lines.append(f"- **{s.raw_citation}**{status_tag}")
                md_lines.append(f"  *Canonical Title:* {s.correct_title}")
                md_lines.append(f"  *Notes:* {s.notes}")
        else:
            md_lines.append("*No explicit statutory sections referenced in provided source text.*")

        md_lines.append("")
        md_lines.append("## 4. Contract Redline & Clause Triage")
        if clause_triage and clause_triage.clauses:
            md_lines.append(f"**Risk Level:** {clause_triage.risk_level} ({clause_triage.overall_risk_score}/100)")
            md_lines.append(f"*(Red: {clause_triage.red_count} | Amber: {clause_triage.amber_count} | Green: {clause_triage.green_count})*")
            md_lines.append("")
            for c in clause_triage.clauses[:4]:
                md_lines.append(f"### [{c.risk_tier}] {c.title} ({c.category_name})")
                for issue in c.issues:
                    md_lines.append(f"- *Issue:* {issue}")
                if c.diff:
                    md_lines.append("```diff")
                    md_lines.append(c.diff.unified_diff)
                    md_lines.append("```")
        else:
            md_lines.append("*No contract clauses triaged.*")

        md_lines.append("")
        md_lines.append("## 5. Limitation Deadlines & Strategic Action Items")
        for act in action_items:
            target_str = f" (Deadline: {act.target_date})" if act.target_date else ""
            md_lines.append(f"- **[{act.urgency}] {act.action}**{target_str}")
            md_lines.append(f"  *Rationale:* {act.deadline_description}")
            if act.statutory_limitation:
                md_lines.append(f"  *Limitation Ground:* {act.statutory_limitation}")

        formatted_md = "\n".join(md_lines)

        return LegalBrief(
            title=title,
            court_forum=court_forum,
            jurisdiction=jurisdiction,
            executive_summary=exec_summary,
            questions_of_law=questions,
            statutory_provisions=statutes,
            governing_precedents=precedents,
            clause_triage=clause_triage,
            action_items=action_items,
            formatted_markdown=formatted_md,
        )
