from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.graph.knowledge_graph import KnowledgeGraph, get_knowledge_graph

logger = logging.getLogger(__name__)


class ConflictDetector:
    """
    Analyzes legal knowledge graphs and project dependency structures
    for semantic conflicts, overruled precedents, contradictory statutory terms,
    and circular dependencies.
    """

    def __init__(self, graph: Optional[KnowledgeGraph] = None):
        self.graph = graph or get_knowledge_graph()

    def detect_overruled_precedents(self, cited_case_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Checks if any cited precedent has been overruled by a subsequent apex or high court judgment.
        """
        overruled_alerts = []
        for case_id in cited_case_ids:
            # Check incoming OVERRULES edges (i.e. other_case -> OVERRULES -> this_case)
            edges = self.graph.local_graph.get_edges(target=case_id, edge_type="OVERRULES")
            for e in edges:
                overruling_node = self.graph.local_graph.get_node(e.source)
                overruled_node = self.graph.local_graph.get_node(case_id)
                overruled_alerts.append({
                    "type": "overruled_precedent",
                    "severity": "CRITICAL",
                    "overruled_case_id": case_id,
                    "overruled_case_title": (
                        overruled_node.properties.get("title", case_id)
                        if overruled_node
                        else case_id
                    ),
                    "overruling_case_id": e.source,
                    "overruling_case_title": (
                        overruling_node.properties.get("title", e.source)
                        if overruling_node
                        else e.source
                    ),
                    "court": (
                        overruling_node.properties.get("court", "Apex Court")
                        if overruling_node
                        else "Apex Court"
                    ),
                    "year": (
                        overruling_node.properties.get("year", "Recent")
                        if overruling_node
                        else "Recent"
                    ),
                    "reason": e.properties.get("reason", "Overruled on constitutional/statutory grounds"),
                    "recommendation": (
                        f"Do not rely on {case_id}. Substitute with governing precedent "
                        f"{overruling_node.properties.get('title', e.source) if overruling_node else e.source}."
                    ),
                })
        return overruled_alerts

    def detect_clause_statute_conflicts(
        self, clause_id: str, clause_text: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Evaluates explicit graph conflict relationships and heuristic statutory barriers:
        - Section 27 Indian Contract Act (Agreement in restraint of trade void)
        - Section 28 Indian Contract Act (Agreement in restraint of legal proceedings void)
        - Section 23 Indian Contract Act (Unlawful consideration and objects)
        """
        conflicts = []
        # Check explicit graph CONFLICTS_WITH edges
        edges = self.graph.local_graph.get_edges(source=clause_id, edge_type="CONFLICTS_WITH")
        for e in edges:
            target_node = self.graph.local_graph.get_node(e.target)
            conflicts.append({
                "type": "statutory_inconsistency",
                "severity": "HIGH",
                "clause_id": clause_id,
                "conflicting_target": e.target,
                "target_type": target_node.type if target_node else "Statute",
                "target_title": target_node.properties.get("act_name", e.target) if target_node else e.target,
                "reason": e.properties.get("reason", "Violates statutory restriction"),
            })

        # Heuristic checks on clause text
        text_lower = (clause_text or "").lower()
        if "shall not practice" in text_lower or "restrained from engaging in any business" in text_lower:
            conflicts.append({
                "type": "potential_statutory_violation",
                "severity": "CRITICAL",
                "clause_id": clause_id,
                "statute_reference": "Section 27, Indian Contract Act 1872",
                "reason": "Post-termination absolute non-compete covenants are generally void under Section 27.",
                "recommendation": "Limit covenant to non-solicitation of clients and confidentiality protection.",
            })

        if "waives all rights to approach court" in text_lower or "precluded from arbitration" in text_lower:
            conflicts.append({
                "type": "potential_statutory_violation",
                "severity": "CRITICAL",
                "clause_id": clause_id,
                "statute_reference": "Section 28, Indian Contract Act 1872",
                "reason": "Agreements absolutely restricting enforcement of legal rights are void under Section 28.",
                "recommendation": "Implement standard tiered dispute resolution (Negotiation -> Mediation -> Arbitration).",
            })

        return conflicts

    def detect_circular_dependencies(
        self, edge_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detects circular dependencies in code project structures or clause references.
        """
        types = edge_types or ["DEPENDS_ON", "REFERENCES"]
        cycles = self.graph.local_graph.find_cycles(types)
        cycle_reports = []
        for cycle in cycles:
            cycle_reports.append({
                "type": "circular_dependency",
                "severity": "MEDIUM",
                "path": cycle,
                "description": f"Circular loop detected: {' -> '.join(cycle)}",
            })
        return cycle_reports

    def run_full_audit(self) -> Dict[str, Any]:
        """Runs a complete conflict audit across all precedents, clauses, and project files."""
        # Find all precedents
        precedents = self.graph.local_graph.get_nodes_by_type("Precedent")
        precedent_ids = [p.id for p in precedents]
        overruled = self.detect_overruled_precedents(precedent_ids)

        # Find all clauses
        clauses = self.graph.local_graph.get_nodes_by_type("ContractClause")
        clause_conflicts = []
        for c in clauses:
            cf = self.detect_clause_statute_conflicts(c.id, c.properties.get("text", ""))
            clause_conflicts.extend(cf)

        # Cycles
        cycles = self.detect_circular_dependencies()

        return {
            "total_conflicts": len(overruled) + len(clause_conflicts) + len(cycles),
            "overruled_precedents": overruled,
            "clause_conflicts": clause_conflicts,
            "circular_dependencies": cycles,
        }
