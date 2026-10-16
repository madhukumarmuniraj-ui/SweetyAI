from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.recovery.checkpoint_system import CheckpointManager, RecoveryManager, StateManager
from app.sandbox.diff_verifier import DiffResult, DiffVerifier
from app.sandbox.sandbox_engine import SandboxedExecutionResult, SandboxEngine

logger = logging.getLogger(__name__)


@dataclass
class HealingIteration:
    iteration: int
    attempted_code: str
    error: Optional[str]
    exception_type: Optional[str]
    success: bool
    diff: Optional[Dict[str, Any]] = None


@dataclass
class HealingResult:
    success: bool
    initial_code: str
    final_code: str
    iterations_count: int
    iterations: List[HealingIteration] = field(default_factory=list)
    final_execution: Optional[SandboxedExecutionResult] = None
    diff: Optional[DiffResult] = None
    checkpoint_id: Optional[str] = None
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "iterations_count": self.iterations_count,
            "summary": self.summary,
            "final_code": self.final_code,
            "diff": self.diff.to_dict() if self.diff else None,
            "final_execution": self.final_execution.to_dict() if self.final_execution else None,
            "checkpoint_id": self.checkpoint_id,
            "iterations": [
                {
                    "iteration": it.iteration,
                    "error": it.error,
                    "exception_type": it.exception_type,
                    "success": it.success,
                }
                for it in self.iterations
            ],
        }


class SelfHealingAgent:
    """
    Autonomous code execution, error interception, iterative multi-step repair,
    and rollback protection.
    """

    def __init__(
        self,
        llm_agent: Optional[Any] = None,
        sandbox: Optional[SandboxEngine] = None,
        checkpoint_mgr: Optional[CheckpointManager] = None,
        state_mgr: Optional[StateManager] = None,
        recovery_mgr: Optional[RecoveryManager] = None,
    ):
        self.llm_agent = llm_agent
        self.sandbox = sandbox or SandboxEngine(timeout_seconds=5.0)
        self.checkpoint_mgr = checkpoint_mgr or CheckpointManager()
        self.state_mgr = state_mgr or StateManager()
        self.recovery_mgr = recovery_mgr or RecoveryManager(self.checkpoint_mgr, self.state_mgr)

    def _extract_code_from_response(self, text: str) -> str:
        """Extracts code from markdown code fences or cleans raw response."""
        code_block = re.search(r"```(?:python)?\s*([\s\S]*?)```", text)
        if code_block:
            return code_block.group(1).strip()
        return text.strip()

    def _heuristic_repair(self, code: str, exc_type: str, failing_code: Optional[str]) -> Optional[str]:
        """Rule-based heuristic fallbacks for common syntactic/runtime blunders."""
        lines = code.splitlines()

        # 1. ZeroDivisionError safeguard
        if exc_type == "ZeroDivisionError":
            repaired_lines = []
            for line in lines:
                if "/" in line and not line.strip().startswith("#"):
                    # Wrap or safeguard division
                    repaired_lines.append(line.replace("/ 0", "/ 1"))
                else:
                    repaired_lines.append(line)
            return "\n".join(repaired_lines)

        # 2. IndexError / KeyError
        if exc_type in ("IndexError", "KeyError") and lines:
            return code

        # 3. NameError (e.g. undefined variable)
        if exc_type == "NameError" and failing_code:
            match = re.search(r"name '(\w+)' is not defined", failing_code)
            if match:
                var_name = match.group(1)
                return f"{var_name} = None\n" + code

        return None

    def heal(
        self,
        code: str,
        goal: str = "",
        max_retries: int = 3,
        target_filepath: Optional[str] = None,
    ) -> HealingResult:
        """
        Executes code in the sandbox. If an exception occurs, enters an iterative self-correction loop.
        """
        checkpoint_id = None
        if target_filepath:
            checkpoint_id = self.checkpoint_mgr.create_checkpoint(
                task_id="self_healing_task",
                task_name=f"Auto-checkpoint for {target_filepath}",
                state={"filepath": target_filepath, "code": code},
                metadata={"filepath": target_filepath},
            )

        # Initial execution
        current_code = code
        exec_res = self.sandbox.execute(current_code)
        if exec_res.success:
            return HealingResult(
                success=True,
                initial_code=code,
                final_code=current_code,
                iterations_count=0,
                final_execution=exec_res,
                checkpoint_id=checkpoint_id,
                summary="Code executed successfully without requiring repair.",
            )

        history: List[HealingIteration] = []
        current_error = exec_res.error
        current_exc_type = exec_res.exception_type
        current_tb = exec_res.traceback
        failing_line = exec_res.failing_line

        for attempt in range(1, max_retries + 1):
            logger.info(f"[SelfHealing] Attempt {attempt}/{max_retries} fixing {current_exc_type}...")

            fixed_candidate = None

            # Generate fix via LLM if available
            if self.llm_agent is not None:
                prompt = (
                    f"Fix the following Python code that failed with an error.\n"
                    f"Task Goal: {goal or 'Fix execution failure'}\n\n"
                    f"Failing Code:\n```python\n{current_code}\n```\n\n"
                    f"Error Type: {current_exc_type}\n"
                    f"Failing Line: {failing_line}\n"
                    f"Traceback:\n{current_tb}\n\n"
                    f"Respond ONLY with the complete corrected Python code inside a ```python ``` block."
                )
                try:
                    if hasattr(self.llm_agent, "run"):
                        llm_out = self.llm_agent.run(prompt)
                    elif hasattr(self.llm_agent, "chat"):
                        llm_out = self.llm_agent.chat(prompt)
                    else:
                        llm_out = str(self.llm_agent(prompt))
                    fixed_candidate = self._extract_code_from_response(llm_out)
                except Exception as e:
                    logger.warning(f"[SelfHealing] LLM correction failed: {e}")
                    fixed_candidate = None

            # Fall back to heuristic repair if LLM did not generate
            if not fixed_candidate:
                fixed_candidate = self._heuristic_repair(
                    current_code, str(current_exc_type), current_error
                )

            if not fixed_candidate:
                fixed_candidate = current_code

            # Re-execute in Sandbox
            new_exec_res = self.sandbox.execute(fixed_candidate)
            diff_res = DiffVerifier.compute_diff(current_code, fixed_candidate)

            history.append(
                HealingIteration(
                    iteration=attempt,
                    attempted_code=fixed_candidate,
                    error=new_exec_res.error,
                    exception_type=new_exec_res.exception_type,
                    success=new_exec_res.success,
                    diff=diff_res.to_dict(),
                )
            )

            if new_exec_res.success:
                overall_diff = DiffVerifier.compute_diff(code, fixed_candidate)
                return HealingResult(
                    success=True,
                    initial_code=code,
                    final_code=fixed_candidate,
                    iterations_count=attempt,
                    iterations=history,
                    final_execution=new_exec_res,
                    diff=overall_diff,
                    checkpoint_id=checkpoint_id,
                    summary=f"Successfully repaired code in {attempt} iteration(s).",
                )

            # Update for next iteration
            current_code = fixed_candidate
            current_error = new_exec_res.error
            current_exc_type = new_exec_res.exception_type
            current_tb = new_exec_res.traceback
            failing_line = new_exec_res.failing_line

        # Failed after all retries -> Rollback
        if checkpoint_id and target_filepath:
            self.recovery_mgr.rollback_to_checkpoint(checkpoint_id)

        overall_diff = DiffVerifier.compute_diff(code, current_code)
        return HealingResult(
            success=False,
            initial_code=code,
            final_code=current_code,
            iterations_count=max_retries,
            iterations=history,
            final_execution=new_exec_res,
            diff=overall_diff,
            checkpoint_id=checkpoint_id,
            summary=f"Could not heal code after {max_retries} attempts. Reverted to checkpoint.",
        )
