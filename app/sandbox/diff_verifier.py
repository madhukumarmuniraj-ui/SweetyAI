from __future__ import annotations

import ast
import difflib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


@dataclass
class DiffResult:
    original: str
    modified: str
    filename: str
    unified_diff: str
    additions: int
    deletions: int
    is_valid_syntax: bool
    syntax_error: str = ""
    diff_lines: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "filename": self.filename,
            "unified_diff": self.unified_diff,
            "additions": self.additions,
            "deletions": self.deletions,
            "is_valid_syntax": self.is_valid_syntax,
            "syntax_error": self.syntax_error,
            "diff_lines": self.diff_lines,
        }


class DiffVerifier:
    """
    Computes unified diffs, line change statistics, and structural AST validations
    between original source and candidate patches.
    """

    @staticmethod
    def compute_diff(
        original: str,
        modified: str,
        filename: str = "target_code.py",
    ) -> DiffResult:
        orig_lines = original.splitlines(keepends=True)
        mod_lines = modified.splitlines(keepends=True)

        diff_gen = difflib.unified_diff(
            orig_lines,
            mod_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
            n=3,
        )
        unified_diff_str = "".join(diff_gen)

        # Count additions / deletions and prepare structured line items for UI
        additions = 0
        deletions = 0
        structured_lines = []

        for line in unified_diff_str.splitlines():
            if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
                structured_lines.append({"type": "header", "text": line})
            elif line.startswith("+"):
                additions += 1
                structured_lines.append({"type": "addition", "text": line[1:]})
            elif line.startswith("-"):
                deletions += 1
                structured_lines.append({"type": "deletion", "text": line[1:]})
            else:
                structured_lines.append({"type": "context", "text": line[1:] if line.startswith(" ") else line})

        # Validate syntax of modified code
        is_valid = True
        syntax_err_msg = ""
        try:
            ast.parse(modified)
        except SyntaxError as e:
            is_valid = False
            syntax_err_msg = f"Line {e.lineno}: {e.msg}"

        return DiffResult(
            original=original,
            modified=modified,
            filename=filename,
            unified_diff=unified_diff_str,
            additions=additions,
            deletions=deletions,
            is_valid_syntax=is_valid,
            syntax_error=syntax_err_msg,
            diff_lines=structured_lines,
        )
