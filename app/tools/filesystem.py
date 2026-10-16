"""Project-relative filesystem tools for SweetyAI.

All operations are confined to the active project root (see app.paths), which
works on both the dev checkout and frozen/portable installs.
"""

from pathlib import Path

from app.paths import project_root


def safe_path(relative_path: str) -> Path:
    """
    Convert a project-relative path into a safe absolute path.
    Prevents access outside the SweetyAI project root.
    """

    root = project_root().resolve()
    raw = Path(relative_path)

    requested = raw.resolve() if raw.is_absolute() else (root / raw).resolve()

    try:
        requested.relative_to(root)
    except ValueError:
        raise PermissionError(
            "Access outside the SweetyAI project is not allowed."
        )

    return requested


def list_files(directory: str = ".") -> str:
    """
    List files and directories inside the SweetyAI project.
    """

    path = safe_path(directory)

    if not path.exists():
        return f"Directory does not exist: {directory}"

    if not path.is_dir():
        return f"Not a directory: {directory}"

    items = []

    for item in sorted(path.iterdir()):
        if item.is_dir():
            items.append(f"[DIR]  {item.name}")
        else:
            items.append(f"[FILE] {item.name}")

    if not items:
        return "(empty directory)"

    return "\n".join(items)


def read_file(path: str) -> str:
    """
    Read a text file inside the SweetyAI project.
    """

    file_path = safe_path(path)

    if not file_path.exists():
        return f"File does not exist: {path}"

    if not file_path.is_file():
        return f"Not a file: {path}"

    # Limit file size for safety.
    if file_path.stat().st_size > 1_000_000:
        return "File is too large to read."

    try:
        return file_path.read_text(
            encoding="utf-8"
        )

    except UnicodeDecodeError:
        return "File is not a UTF-8 text file."
