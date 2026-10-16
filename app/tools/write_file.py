from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def write_file(path: str, content: str) -> str:

    target = (PROJECT_ROOT / path).resolve()

    try:
        target.relative_to(PROJECT_ROOT)
    except ValueError:
        return "Error: Cannot write outside the SweetyAI project."

    if target == PROJECT_ROOT:
        return "Error: Cannot write to the project directory itself."

    try:

        target.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            target,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(content)

        return (
            f"File written successfully: "
            f"{target.relative_to(PROJECT_ROOT)}"
        )

    except Exception as error:

        return f"File write error: {error}"