import pytest

from app.legal.playbook_engine import PlaybookEngine
from app.legal.clause_triager import ClauseTriager
from app.legal.statute_verifier import StatuteVerifier
from app.legal.brief_synthesizer import BriefSynthesizer


def test_playbook_engine_loading_and_splitting():
    engine = PlaybookEngine()
    assert len(engine.rules) >= 6
    assert "limitation_of_liability" in engine.rules
    assert "indemnification" in engine.rules

    sample_contract = """
1. Limitation of Liability
The Vendor's aggregate liability under this agreement shall be unlimited.

Section 2. Indemnification
Vendor shall indemnify Customer against any and all claims whatsoever.

3. Governing Law
This agreement is governed by the laws of India.
"""
    clauses = engine.split_into_clauses(sample_contract)
    assert len(clauses) >= 3

    cat1 = engine.classify_clause(clauses[0]["text"], clauses[0]["title"])
    assert cat1 == "limitation_of_liability"


def test_clause_triager_red_and_green():
    triager = ClauseTriager()

    # Red Tier: Uncapped liability
    red_clause_text = "Vendor shall have unlimited liability for all direct and indirect damages without any cap whatsoever."
    res_red = triager.triage_clause("c1", "Limitation of Liability", red_clause_text)
    assert res_red.risk_tier == "RED"
    assert len(res_red.issues) >= 1
    assert res_red.diff is not None

    # Green Tier: Balanced 12-month fees
    green_clause_text = "Each party's total aggregate liability shall not exceed the total fees paid in the preceding 12 months. Consequential damages are excluded except for gross negligence."
    res_green = triager.triage_clause("c2", "Limitation of Liability", green_clause_text)
    assert res_green.risk_tier == "GREEN"


def test_statute_verifier():
    verifier = StatuteVerifier()

    # Valid active citation
    res1 = verifier.verify_citation("73", "Indian Contract Act, 1872")
    assert res1.is_valid is True
    assert res1.status == "VALID_ACTIVE"
    assert "loss or damage" in res1.notes

    # Repealed Section in Contract Act (Section 80 is in 76-123 range)
    res2 = verifier.verify_citation("80", "Indian Contract Act, 1872")
    assert res2.is_valid is False
    assert res2.status == "REPEALED"

    # Out of range section
    res3 = verifier.verify_citation("999", "Indian Contract Act, 1872")
    assert res3.is_valid is False
    assert res3.status == "INVALID_SECTION"

    # Text scanning
    text = "Under Section 34 of the Arbitration and Conciliation Act, the award is liable to be set aside."
    scan_results = verifier.scan_text(text)
    assert len(scan_results) >= 1
    assert scan_results[0].section == "34"
    assert scan_results[0].is_valid is True


def test_brief_synthesizer():
    synthesizer = BriefSynthesizer()

    sample_brief_text = """
The Claimant seeks to challenge the arbitral award under Section 34 of the Arbitration and Conciliation Act 1996.
The underlying contract contained Section 1. Limitation of Liability providing for unlimited liability.
Notice of dispute was served with a 30-day cure period.
Whether the arbitrator erred in awarding consequential damages under Section 73 of the Indian Contract Act?
"""
    brief = synthesizer.synthesize_brief(
        title="Commercial Arbitral Award Challenge",
        document_text=sample_brief_text,
        court_forum="High Court of Delhi",
    )

    assert brief.title == "Commercial Arbitral Award Challenge"
    assert len(brief.statutory_provisions) >= 2
    assert len(brief.action_items) >= 1
    assert len(brief.questions_of_law) >= 1
    assert "# LEGAL BRIEF:" in brief.formatted_markdown
