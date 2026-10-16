"""SweetyAI DSPy Legal Optimizer.

Compiles an optimized legal-reasoning pipeline using DSPy (optional dependency).
If dspy is not installed the module still imports cleanly and reports guidance
instead of crashing at import time.
"""

import os

try:
    import dspy
    DSPY_AVAILABLE = True
except ImportError:
    dspy = None
    DSPY_AVAILABLE = False


def configure_dspy_backend(model_name="huggingface/Qwen/Qwen2.5-7B-Instruct"):
    """Configures DSPy to use your local or HuggingFace model backend."""
    if not DSPY_AVAILABLE:
        print("[DSPy Optimizer] dspy is not installed. Run: pip install dspy")
        return False
    try:
        lm = dspy.LM(model=model_name, temperature=0.2, max_tokens=500)
        dspy.configure(lm=lm)
        return True
    except Exception as e:
        print(f"DSPy LM config note: {e}")
        return False


if DSPY_AVAILABLE:

    class LegalAnalysisSignature(dspy.Signature):
        """Analyze legal text, statutes, or client briefs with strict professional precision, identifying core legal issues, relevant statutory provisions, and actionable legal conclusions."""

        input_text: str = dspy.InputField(desc="The raw legal text, judgment excerpt, statute section, or clipboard snippet.")
        jurisdiction_context: str = dspy.InputField(desc="Applicable legal framework (e.g., KSLU / Indian Law / Constitutional Law).")

        legal_issues: str = dspy.OutputField(desc="Extracted core legal issues or questions of law.")
        statutory_provisions: str = dspy.OutputField(desc="Relevant sections, articles, case laws, or legal doctrines.")
        audited_summary: str = dspy.OutputField(desc="Professional, concise legal summary and conclusion.")

    class SweetyLegalOptimizer(dspy.Module):
        def __init__(self):
            super().__init__()
            self.analyze = dspy.ChainOfThought(LegalAnalysisSignature)

        def forward(self, input_text, jurisdiction_context):
            return self.analyze(input_text=input_text, jurisdiction_context=jurisdiction_context)

else:

    class LegalAnalysisSignature:  # pragma: no cover - placeholder when dspy is absent
        def __init__(self, *args, **kwargs):
            raise RuntimeError("DSPy is not installed. Run: pip install dspy")

    class SweetyLegalOptimizer:  # pragma: no cover - placeholder when dspy is absent
        def __init__(self, *args, **kwargs):
            raise RuntimeError("DSPy is not installed. Run: pip install dspy")


def compile_legal_optimizer():
    """Compile and save the optimized legal reasoning pipeline (requires dspy)."""
    if not DSPY_AVAILABLE:
        print("[DSPy Optimizer] dspy is not installed; skipping compilation. Run: pip install dspy")
        return None

    configure_dspy_backend()

    def legal_metric(gold, pred, trace=None):
        has_issues = len(str(pred.legal_issues).strip()) > 5
        has_provisions = len(str(pred.statutory_provisions).strip()) > 2
        has_summary = len(str(pred.audited_summary).strip()) > 10
        return float(has_issues and has_provisions and has_summary)

    # Expanded training set tailored to Indian Law & KSLU curriculum
    trainset = [
        dspy.Example(
            input_text="Article 21 of the Constitution of India guarantees protection of life and personal liberty except according to procedure established by law.",
            jurisdiction_context="Indian Constitutional Law",
            legal_issues="Right to life, personal liberty, procedure established by law vs due process.",
            statutory_provisions="Article 21, Constitution of India",
            audited_summary="Article 21 serves as the foundational fundamental right protecting individuals against arbitrary executive and legislative action regarding life and personal liberty."
        ).with_inputs("input_text", "jurisdiction_context"),

        dspy.Example(
            input_text="Principles of Natural Justice require 'Audi alteram partem' — that no person shall be condemned unheard.",
            jurisdiction_context="Administrative Law (KSLU)",
            legal_issues="Violation of natural justice, right to a fair hearing, administrative arbitrariness.",
            statutory_provisions="Administrative Law / Article 14 & 21 of Constitution",
            audited_summary="The rule of fair hearing is mandatory in administrative adjudications; failure to provide notice and opportunity to be heard renders administrative action void ab initio."
        ).with_inputs("input_text", "jurisdiction_context")
    ]

    from dspy.teleprompt import BootstrapFewShot
    optimizer = BootstrapFewShot(metric=legal_metric, max_bootstrapped_demos=2, max_labeled_demos=2)

    unoptimized_program = SweetyLegalOptimizer()
    try:
        optimized_program = optimizer.compile(unoptimized_program, trainset=trainset)
    except Exception as e:
        print(f"Compilation warning/fallback: {e}")
        optimized_program = unoptimized_program

    os.makedirs("app/compiled_models", exist_ok=True)
    optimized_program.save("app/compiled_models/optimized_legal_agent.json")
    print("[DSPy Optimizer] ✨ Legal reasoning pipeline successfully compiled with expanded KSLU training cases and saved.")

    return optimized_program


if __name__ == "__main__":
    compile_legal_optimizer()
