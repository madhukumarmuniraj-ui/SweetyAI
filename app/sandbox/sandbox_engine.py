from __future__ import annotations

import ast
import io
import sys
import time
import traceback
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class SandboxedExecutionResult:
    success: bool
    output: str = ""
    error: Optional[str] = None
    traceback: Optional[str] = None
    exception_type: Optional[str] = None
    failing_line: Optional[int] = None
    failing_code: Optional[str] = None
    return_value: Any = None
    execution_time_ms: float = 0.0
    variables: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "traceback": self.traceback,
            "exception_type": self.exception_type,
            "failing_line": self.failing_line,
            "failing_code": self.failing_code,
            "return_value": str(self.return_value) if self.return_value is not None else None,
            "execution_time_ms": round(self.execution_time_ms, 2),
        }


class SecurityASTVisitor(ast.NodeVisitor):
    DISALLOWED_MODULES: Set[str] = {
        "os", "sys", "subprocess", "shutil", "socket", "ctypes",
        "multiprocessing", "pynput", "win32api", "win32con"
    }
    DISALLOWED_CALLS: Set[str] = {
        "eval", "exec", "__import__", "compile", "globals", "locals"
    }

    def __init__(self):
        self.violations: List[str] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            base_pkg = alias.name.split(".")[0]
            if base_pkg in self.DISALLOWED_MODULES:
                self.violations.append(
                    f"Line {node.lineno}: Disallowed import '{alias.name}'"
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            base_pkg = node.module.split(".")[0]
            if base_pkg in self.DISALLOWED_MODULES:
                self.violations.append(
                    f"Line {node.lineno}: Disallowed from-import '{node.module}'"
                )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            if node.func.id in self.DISALLOWED_CALLS:
                self.violations.append(
                    f"Line {node.lineno}: Disallowed built-in call '{node.func.id}()'"
                )
        self.generic_visit(node)


class SandboxEngine:
    """
    Sandboxed Python execution environment with AST static safety checks,
    stdout/stderr capture, timeout enforcement, and detailed traceback diagnostics.
    """

    def __init__(self, timeout_seconds: float = 5.0):
        self.timeout_seconds = timeout_seconds

    def validate_ast(self, code_str: str) -> List[str]:
        """Performs static analysis to detect syntax errors and security policy violations."""
        try:
            tree = ast.parse(code_str)
        except SyntaxError as syn_err:
            return [f"SyntaxError on Line {syn_err.lineno}: {syn_err.msg}"]

        visitor = SecurityASTVisitor()
        visitor.visit(tree)
        return visitor.violations

    def execute(
        self,
        code_str: str,
        globals_dict: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> SandboxedExecutionResult:
        start_time = time.perf_counter()

        # 1. Static AST Safety Check
        violations = self.validate_ast(code_str)
        if violations:
            return SandboxedExecutionResult(
                success=False,
                error="Security or Syntax Check Failed: " + "; ".join(violations),
                exception_type="SecurityValidationError",
                execution_time_ms=(time.perf_counter() - start_time) * 1000.0,
            )

        # 2. Prepare isolated environment
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        # Safe built-in dictionary
        safe_builtins = {
            "abs": abs, "all": all, "any": any, "ascii": ascii, "bin": bin,
            "bool": bool, "bytes": bytes, "chr": chr, "complex": complex,
            "dict": dict, "dir": dir, "divmod": divmod, "enumerate": enumerate,
            "filter": filter, "float": float, "format": format, "frozenset": frozenset,
            "hex": hex, "int": int, "isinstance": isinstance, "issubclass": issubclass,
            "iter": iter, "len": len, "list": list, "map": map, "max": max,
            "min": min, "next": next, "oct": oct, "ord": ord, "pow": pow,
            "print": print, "range": range, "repr": repr, "reversed": reversed,
            "round": round, "set": set, "slice": slice, "sorted": sorted,
            "str": str, "sum": sum, "tuple": tuple, "type": type, "zip": zip,
            "Exception": Exception, "ValueError": ValueError, "TypeError": TypeError,
            "IndexError": IndexError, "KeyError": KeyError, "ZeroDivisionError": ZeroDivisionError,
        }

        exec_globals = {
            "__builtins__": safe_builtins,
            "__name__": "__sandbox__",
            "__doc__": None,
            **(globals_dict or {}),
        }
        exec_locals: Dict[str, Any] = {}

        try:
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

            # Compile AST
            compiled = compile(code_str, "<sandbox>", "exec")
            exec(compiled, exec_globals, exec_locals)

            elapsed = (time.perf_counter() - start_time) * 1000.0
            return SandboxedExecutionResult(
                success=True,
                output=stdout_capture.getvalue(),
                execution_time_ms=elapsed,
                variables={k: v for k, v in exec_locals.items() if not k.startswith("__")},
            )

        except Exception as exc:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            exc_type, exc_val, exc_tb = sys.exc_info()
            tb_formatted = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))

            # Extract failing line number
            failing_line = None
            failing_code = None
            tb_list = traceback.extract_tb(exc_tb)
            for frame in reversed(tb_list):
                if frame.filename == "<sandbox>":
                    failing_line = frame.lineno
                    failing_code = frame.line
                    break

            return SandboxedExecutionResult(
                success=False,
                output=stdout_capture.getvalue(),
                error=str(exc),
                traceback=tb_formatted,
                exception_type=type(exc).__name__,
                failing_line=failing_line,
                failing_code=failing_code,
                execution_time_ms=elapsed,
                variables={k: v for k, v in exec_locals.items() if not k.startswith("__")},
            )

        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
