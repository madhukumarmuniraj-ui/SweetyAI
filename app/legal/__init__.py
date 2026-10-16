"""
Specialized Local Legal Copilot Subsystem for SweetyAI.
Includes playbook-driven contract redlining, clause triage (Red/Amber/Green),
deterministic statutory verification, and structured brief synthesis.
"""

from app.legal.playbook_engine import PlaybookEngine, ClauseRule
from app.legal.clause_triager import ClauseTriager, ClauseTriageResult, ContractTriageReport
from app.legal.statute_verifier import StatuteVerifier, CitationVerificationResult
from app.legal.brief_synthesizer import BriefSynthesizer, LegalBrief

__all__ = [
    "PlaybookEngine",
    "ClauseRule",
    "ClauseTriager",
    "ClauseTriageResult",
    "ContractTriageReport",
    "StatuteVerifier",
    "CitationVerificationResult",
    "BriefSynthesizer",
    "LegalBrief",
]
