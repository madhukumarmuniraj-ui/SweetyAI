from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[2]

IGNORED_DIRECTORIES = {
    ".venv",
    "__pycache__",
    ".git",
    "searxng",
}


def search_project(query: str, mode: str = "text") -> str:
    query = query.strip()

    # Normalize escaped characters commonly produced in tool-call JSON.
    query = (
        query
        .replace(r'\"', '"')
        .replace(r"\[", "[")
        .replace(r"\]", "]")
    )

    mode = mode.strip().lower()

    if not query:
        return "Search query was empty."

    search_name = query.rsplit(".", 1)[-1]

    if mode not in {
        "text",
        "definition",
        "usage",
        "import",
        "registration",
    }:
        return (
            "Invalid search mode. Use: text, definition, "
            "usage, import, or registration."
        )

    results = []

    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file():
            continue

        relative = path.relative_to(PROJECT_ROOT)

        if any(
            part in IGNORED_DIRECTORIES
            for part in relative.parts
        ):
            continue

        if path.suffix not in {
            ".py",
            ".txt",
            ".md",
            ".json",
            ".yml",
            ".yaml",
        }:
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        lines = text.splitlines()

        for line_number, line in enumerate(lines, start=1):
            stripped = line.strip()

            if not stripped:
                continue

            if stripped.startswith("#"):
                continue

            matched = False

            if mode == "text":
                matched = query.lower() in line.lower()

            elif mode == "definition":
                active_module = None

                tools_file = (
                    PROJECT_ROOT
                    / "app"
                    / "agent"
                    / "tools.py"
                )

                try:
                    tools_text = tools_file.read_text(
                        encoding="utf-8"
                    )

                    import_match = re.search(
                        rf"from\s+([A-Za-z0-9_.]+)\s+import\s+"
                        rf"{re.escape(search_name)}\b",
                        tools_text,
                    )

                    if import_match:
                        active_module = import_match.group(1)

                except (UnicodeDecodeError, OSError):
                    active_module = None

                if active_module:
                    active_path = (
                        PROJECT_ROOT
                        / Path(*active_module.split("."))
                    ).with_suffix(".py")

                    if active_path.exists():
                        try:
                            active_text = active_path.read_text(
                                encoding="utf-8"
                            )

                            for (
                                active_line_number,
                                active_line,
                            ) in enumerate(
                                active_text.splitlines(),
                                start=1,
                            ):
                                if re.search(
                                    rf"\bdef\s+"
                                    rf"{re.escape(search_name)}\s*\(",
                                    active_line,
                                ):
                                    return (
                                        f"{active_path.relative_to(PROJECT_ROOT)}:"
                                        f"{active_line_number}: "
                                        f"{active_line.strip()}"
                                    )

                        except (UnicodeDecodeError, OSError):
                            pass

                patterns = [
                    rf"\bclass\s+{re.escape(search_name)}\b",
                    rf"\bdef\s+{re.escape(search_name)}\s*\(",
                ]

                matched = any(
                    re.search(pattern, line)
                    for pattern in patterns
                )

            elif mode == "usage":
                call_patterns = [
                    rf"\b{re.escape(search_name)}\s*\(",
                    rf"\bself\.{re.escape(search_name)}\s*\(",
                ]

                if "." in query:
                    call_patterns.append(
                        rf"\b{re.escape(query)}\s*\("
                    )

                if any(
                    re.search(pattern, line)
                    for pattern in call_patterns
                ):
                    if re.match(
                        r"^\s*(def|async\s+def)\s+",
                        line,
                    ):
                        continue

                    if re.match(
                        r"^\s*(from|import)\s+",
                        line,
                    ):
                        continue

                    usage_lines = [stripped]

                    open_parens = (
                        line.count("(")
                        - line.count(")")
                    )

                    next_index = line_number

                    while (
                        open_parens > 0
                        and next_index < len(lines)
                    ):
                        next_line = lines[next_index]

                        usage_lines.append(
                            next_line.strip()
                        )

                        open_parens += (
                            next_line.count("(")
                            - next_line.count(")")
                        )

                        next_index += 1

                    results.append(
                        f"{relative}:{line_number}: "
                        + "\n".join(usage_lines)
                    )

                    if len(results) >= 50:
                        return (
                            "\n".join(results)
                            + "\n\n[Results limited to 50 matches.]"
                        )

                    continue

            elif mode == "import":
                matched = (
                    f"import {query}" in line
                    or f"from {query}" in line
                )

            elif mode == "registration":
                if "registry.register(" in line:
                    for next_index in range(
                        line_number - 1,
                        min(
                            line_number + 30,
                            len(lines),
                        ),
                    ):
                        registration_line = lines[next_index]

                        match = re.search(
                            r'name\s*=\s*["\']([^"\']+)["\']',
                            registration_line,
                        )

                        if not match:
                            match = re.search(
                                r'registry\.register\(\s*'
                                r'["\']([^"\']+)["\']',
                                registration_line,
                            )

                        if match:
                            registered_name = match.group(1)

                            if (
                                query == "registry.register"
                                or query == registered_name
                            ):
                                results.append(
                                    f"{relative}:{next_index + 1}: "
                                    f"registered tool: "
                                    f"{registered_name}"
                                )

                            break

                    continue

            if matched:
                results.append(
                    f"{relative}:{line_number}: {stripped}"
                )

                if len(results) >= 50:
                    return (
                        "\n".join(results)
                        + "\n\n[Results limited to 50 matches.]"
                    )

    if not results:
        return f"No {mode} matches found for: {query}"

    return "\n".join(results)