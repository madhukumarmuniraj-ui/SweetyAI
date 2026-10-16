import subprocess
import webbrowser
from pathlib import Path

from app.paths import project_root

PROJECT_ROOT = project_root()

MAX_OUTPUT_CHARS = 20000
DEFAULT_TIMEOUT_SECONDS = 60


def _safe_dir(path: str) -> Path:
    """Resolve a project-relative directory, rejecting paths outside the project."""
    target = (PROJECT_ROOT / (path or ".")).resolve()

    try:
        target.relative_to(PROJECT_ROOT)
    except ValueError:
        raise PermissionError("Access outside the SweetyAI project is not allowed.")

    return target


def run_command(command: str, cwd: str = ".") -> str:
    """
    Run a shell command inside the SweetyAI project and return its output.
    Suitable for build, test, git, and package-manager commands.
    """
    if not command or not command.strip():
        return "Error: command was empty."

    workdir = _safe_dir(cwd)

    if not workdir.exists():
        return f"Error: directory does not exist: {cwd}"

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(workdir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {DEFAULT_TIMEOUT_SECONDS}s: {command}"
    except Exception as error:
        return f"Error running command: {error}"

    output = result.stdout or ""
    if result.stderr:
        output = (output + "\n[stderr]\n" + result.stderr).strip()

    output = output.strip() or "(no output)"

    if len(output) > MAX_OUTPUT_CHARS:
        output = output[:MAX_OUTPUT_CHARS] + "\n...[output truncated]"

    return f"exit code: {result.returncode}\n{output}"


def git_status(path: str = ".") -> str:
    """Return `git status --short --branch` for the project (or a subdirectory)."""
    workdir = _safe_dir(path)

    if not (workdir / ".git").exists() and not (PROJECT_ROOT / ".git").exists():
        return "Not a git repository."

    return run_command("git status --short --branch", cwd=path)


def git_diff(path: str = ".") -> str:
    """Return the current unstaged git diff for the project."""
    workdir = _safe_dir(path)

    if not (workdir / ".git").exists() and not (PROJECT_ROOT / ".git").exists():
        return "Not a git repository."

    return run_command("git diff", cwd=path)


def edit_file(path: str, old_text: str, new_text: str) -> str:
    """
    Replace an exact text block inside a project file.
    Fails if old_text is missing or matches more than once (forces a precise match).
    """
    if not old_text:
        return "Error: old_text was empty."

    target = (PROJECT_ROOT / path).resolve()

    try:
        target.relative_to(PROJECT_ROOT)
    except ValueError:
        return "Error: Cannot edit outside the SweetyAI project."

    if not target.exists():
        return f"Error: file does not exist: {path}"

    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "Error: file is not UTF-8 text."

    matches = content.count(old_text)

    if matches == 0:
        return "Error: old_text not found in file. Read the file and retry with the exact text."
    if matches > 1:
        return f"Error: old_text matches {matches} times. Provide more surrounding context."

    updated = content.replace(old_text, new_text, 1)

    try:
        target.write_text(updated, encoding="utf-8")
    except Exception as error:
        return f"Error writing file: {error}"

    return f"Edited {path}: replaced {len(old_text)} chars with {len(new_text)} chars."


def open_url(url: str) -> str:
    """Open an http/https URL in the default browser."""
    if not url.startswith(("http://", "https://")):
        return "Error: only http:// or https:// URLs can be opened."

    try:
        webbrowser.open(url)
    except Exception as error:
        return f"Error opening URL: {error}"

    return f"Opened {url} in the default browser."
