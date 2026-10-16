"""Unit tests for the SweetyAI core subsystems (graph, sandbox, legal, adaptive).

These exercise the modules directly (KnowledgeGraph, SandboxEngine, ClauseTriager,
StatuteVerifier, DryRunPatcher, biometric cadence + persona engine) — no HTTP
server required.
"""

import os

from app.graph.knowledge_graph import KnowledgeGraph
from app.sandbox.sandbox_engine import SandboxEngine
from app.legal.clause_triager import ClauseTriager
from app.legal.statute_verifier import StatuteVerifier
from app.adaptive.dry_run_patcher import DryRunPatcher
from app.adaptive.biometric_cadence import BiometricCadenceModel
from app.adaptive.persona_engine import PersonaEngine


# ---------------------------------------------------------------------------
# Knowledge Graph
# ---------------------------------------------------------------------------

def test_knowledge_graph_nodes_and_search(tmp_path):
    kg = KnowledgeGraph(storage_path=str(tmp_path / "kg.json"))
    kg.add_node("TEST_STATUTE_API", "Statute", {"title": "Test Arbitration Statute"})

    stats = kg.get_stats()
    assert stats["total_nodes"] >= 1
    assert "neo4j_active" in stats

    results = kg.search("Arbitration")
    assert len(results) >= 1
    assert any("TEST_STATUTE_API" == r.get("id") for r in results)


def test_knowledge_graph_statute_and_edge(tmp_path):
    kg = KnowledgeGraph(storage_path=str(tmp_path / "kg2.json"))
    kg.add_statute("S73_ICA", act_name="Indian Contract Act", section="73",
                   text="Compensation for loss or damage caused by breach of contract.")
    kg.add_node("CLAUSE_C1", "Clause", {"title": "Damages clause"})
    kg.link_entities("CLAUSE_C1", "S73_ICA", "CITES")

    statutes = kg.find_statutes_for_clause("CLAUSE_C1")
    assert any(s.get("id") == "S73_ICA" for s in statutes)


# ---------------------------------------------------------------------------
# Sandbox Engine
# ---------------------------------------------------------------------------

def test_sandbox_executes_safe_code():
    engine = SandboxEngine()
    result = engine.execute("x = 2 + 3\nprint(x)")
    assert result.success is True
    assert "5" in result.output


def test_sandbox_blocks_disallowed_import():
    engine = SandboxEngine()
    violations = engine.validate_ast("import os")
    assert violations, "import os should be flagged by the security AST visitor"

    result = engine.execute("import os\nprint('nope')")
    assert result.success is False
    assert result.exception_type == "SecurityValidationError"


# ---------------------------------------------------------------------------
# Clause Triager
# ---------------------------------------------------------------------------

def test_clause_triage_flags_red_risk():
    triager = ClauseTriager()
    contract_text = "The consultant agrees to infinite indemnification liability for any loss."
    report = triager.triage_contract(contract_text)
    assert report.red_count >= 1
    assert report.total_clauses >= 1
    assert report.risk_level in ("HIGH", "MODERATE", "LOW")


# ---------------------------------------------------------------------------
# Statute Verifier
# ---------------------------------------------------------------------------

def test_statute_verifier_valid_citation():
    verifier = StatuteVerifier()
    result = verifier.verify_citation("73", "Indian Contract Act")
    assert result.is_valid is True
    assert "Indian Contract Act" in result.correct_title


def test_statute_verifier_out_of_range_section():
    verifier = StatuteVerifier()
    result = verifier.verify_citation("99999", "Indian Contract Act")
    assert result.is_valid is False
    assert result.status in ("INVALID_SECTION", "UNKNOWN_ACT")


# ---------------------------------------------------------------------------
# Dry Run Patcher
# ---------------------------------------------------------------------------

def test_dry_run_patch_preview_and_apply(tmp_path):
    test_file = tmp_path / "code.py"
    test_file.write_text("def foo():\n    return 42\n")

    patcher = DryRunPatcher()

    preview = patcher.preview_patch(str(test_file), "def foo():\n    return 100\n")
    assert preview.lines_changed >= 1
    assert preview.checksum_before != preview.checksum_after

    result = patcher.apply_patch(str(test_file), "def foo():\n    return 100\n")
    assert result["ok"] is True
    assert test_file.read_text() == "def foo():\n    return 100\n"


def test_dry_run_patch_creates_new_file(tmp_path):
    new_file = tmp_path / "brand_new.py"
    patcher = DryRunPatcher()
    preview = patcher.preview_patch(str(new_file), "print('hello')\n")
    assert preview.is_new_file is True


# ---------------------------------------------------------------------------
# Adaptive Cadence + Persona
# ---------------------------------------------------------------------------

def test_biometric_cadence_analyzes_events():
    model = BiometricCadenceModel()
    events = [
        {"key": "a", "timestamp": 1000.0},
        {"key": "b", "timestamp": 1100.0},
        {"key": "c", "timestamp": 1200.0},
        {"key": "d", "timestamp": 1300.0},
    ]
    metrics = model.analyze_keystroke_series(events, duration_ms=300.0)
    assert metrics.total_keystrokes == 4
    assert isinstance(metrics.cognitive_state, str) and metrics.cognitive_state


def test_persona_transitions_from_cadence():
    model = BiometricCadenceModel()
    events = [
        {"key": "a", "timestamp": 1000.0},
        {"key": "b", "timestamp": 1080.0},
        {"key": "c", "timestamp": 1160.0},
        {"key": "d", "timestamp": 1240.0},
    ]
    metrics = model.analyze_keystroke_series(events, duration_ms=240.0)

    persona_engine = PersonaEngine()
    state = persona_engine.transition_from_cadence(metrics)
    assert state is not None
    assert "name" in state.to_dict()
