import os
import tempfile
import pytest

from app.graph.local_graph import LocalSemanticGraph, Node, Edge
from app.graph.knowledge_graph import KnowledgeGraph
from app.graph.conflict_detector import ConflictDetector
from app.graph.hybrid_retriever import HybridRetriever


def test_local_semantic_graph_nodes_edges():
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, "test_graph.json")
        graph = LocalSemanticGraph(json_path)

        # Add nodes
        n1 = graph.add_node("s73_ica", "Statute", {"act_name": "Indian Contract Act", "section": "73"})
        n2 = graph.add_node("hadley_v_baxendale", "Precedent", {"title": "Hadley v Baxendale", "year": 1854})

        assert n1.id == "s73_ica"
        assert graph.get_node("s73_ica") is not None
        assert len(graph.get_nodes_by_type("Statute")) == 1

        # Add edge
        e = graph.add_edge("hadley_v_baxendale", "s73_ica", "CITES", {"notes": "Foundation for remoteness of damages"})
        assert e.source == "hadley_v_baxendale"
        assert e.target == "s73_ica"

        # Traversal
        subgraph = graph.traverse_subgraph("hadley_v_baxendale", max_depth=1)
        assert len(subgraph["nodes"]) == 2
        assert len(subgraph["edges"]) == 1

        # Save and Reload
        assert graph.save_to_json()
        assert os.path.exists(json_path)

        graph2 = LocalSemanticGraph(json_path)
        assert graph2.get_node("s73_ica") is not None
        assert len(graph2.get_nodes_by_type("Precedent")) == 1


def test_cycle_detection():
    graph = LocalSemanticGraph()
    graph.add_edge("fileA.py", "fileB.py", "DEPENDS_ON")
    graph.add_edge("fileB.py", "fileC.py", "DEPENDS_ON")
    graph.add_edge("fileC.py", "fileA.py", "DEPENDS_ON")

    cycles = graph.find_cycles(["DEPENDS_ON"])
    assert len(cycles) > 0
    assert "fileA.py" in cycles[0]


def test_knowledge_graph_facade_and_conflict_detector():
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, "kg_test.json")
        kg = KnowledgeGraph(json_path)

        # Add Statute
        kg.add_statute("s27_ica", "Indian Contract Act 1872", "Section 27", text="Agreement in restraint of trade void")

        # Add Precedents
        kg.add_precedent("percept_dmark", "Percept D'Mark v Zaheer Khan", "AIR 2006 SC 3426", court="Supreme Court", year=2006)
        kg.add_precedent("old_case", "Old Precedent Case", "1950 SC 100", court="High Court", year=1950)

        # Link citations and overruling
        kg.link_precedent_to_statute("percept_dmark", "s27_ica", "Post-contractual covenant validity")
        kg.link_overrules("percept_dmark", "old_case", "Overruled on constitutional doctrine")

        # Add Contract Clause
        kg.add_clause("clause_non_compete", "Non-Compete", "restrictive_covenant", "The employee shall not practice or engage in any business for 5 years")
        kg.link_clause_conflicts("clause_non_compete", "s27_ica", "Violates Section 27 absolute restraint prohibition")

        # Conflict Detector
        detector = ConflictDetector(kg)
        overruled_alerts = detector.detect_overruled_precedents(["old_case"])
        assert len(overruled_alerts) == 1
        assert overruled_alerts[0]["overruling_case_id"] == "percept_dmark"

        clause_conflicts = detector.detect_clause_statute_conflicts(
            "clause_non_compete", "The employee shall not practice or engage in any business"
        )
        assert len(clause_conflicts) >= 1

        stats = kg.get_stats()
        assert stats["total_nodes"] >= 4
        assert stats["total_edges"] >= 3


def test_hybrid_retriever():
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, "hybrid_test.json")
        kg = KnowledgeGraph(json_path)
        kg.add_statute("arbitration_act_s7", "Arbitration and Conciliation Act 1996", "Section 7", text="Arbitration agreement definition")

        retriever = HybridRetriever(kg)
        res = retriever.retrieve("Arbitration agreement definition", n_results=3)
        assert res is not None
        assert "query" in res
        assert "results" in res
        assert "consolidated_context" in res
