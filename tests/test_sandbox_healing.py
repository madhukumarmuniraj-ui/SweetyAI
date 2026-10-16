import os
import tempfile
import pytest

from app.sandbox.sandbox_engine import SandboxEngine
from app.sandbox.diff_verifier import DiffVerifier
from app.sandbox.self_healing_agent import SelfHealingAgent


def test_sandbox_security_blocks():
    sandbox = SandboxEngine()

    # Disallowed os import
    bad_code = "import os\nos.system('echo hi')"
    res = sandbox.execute(bad_code)
    assert not res.success
    assert "Security or Syntax Check Failed" in res.error

    # Disallowed subprocess
    bad_code2 = "import subprocess\nsubprocess.run(['dir'])"
    res2 = sandbox.execute(bad_code2)
    assert not res2.success


def test_sandbox_traceback_capture():
    sandbox = SandboxEngine()

    broken_code = """
x = 10
y = 0
z = x / y
"""
    res = sandbox.execute(broken_code)
    assert not res.success
    assert res.exception_type == "ZeroDivisionError"
    assert res.failing_line == 4
    assert res.traceback is not None


def test_diff_verifier():
    orig = "def add(a, b):\n    return a - b\n"
    fixed = "def add(a, b):\n    return a + b\n"

    diff_res = DiffVerifier.compute_diff(orig, fixed, "calc.py")
    assert diff_res.additions == 1
    assert diff_res.deletions == 1
    assert diff_res.is_valid_syntax is True
    assert "+    return a + b" in diff_res.unified_diff


def test_self_healing_agent_heuristic_repair():
    sandbox = SandboxEngine()
    agent = SelfHealingAgent(sandbox=sandbox)

    broken_code = """
a = 100
b = 0
result = a / 0
print(f"Result is {result}")
"""
    heal_res = agent.heal(broken_code, goal="Safeguard division")
    assert heal_res.success is True
    assert heal_res.iterations_count >= 1
    assert heal_res.diff is not None
    assert heal_res.final_execution is not None
    assert heal_res.final_execution.success is True
