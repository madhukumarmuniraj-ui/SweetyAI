import os
import datetime
import difflib

REDLINE_DIR = "redline_outputs"


def generate_redline(original_path, modified_path):
    os.makedirs(REDLINE_DIR, exist_ok=True)
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    if not os.path.exists(original_path):
        print(f"[Error] Original file '{original_path}' not found.")
        return
    if not os.path.exists(modified_path):
        print(f"[Error] Modified file '{modified_path}' not found.")
        return

    with open(original_path, "r", encoding="utf-8", errors="replace") as f:
        orig_text = f.readlines()

    with open(modified_path, "r", encoding="utf-8", errors="replace") as f:
        mod_text = f.readlines()

    print(f"\n=== SweetyAI Legal Redline & Tracked Change Generator ===")
    print(f"Original File : {original_path}")
    print(f"Modified File : {modified_path}")

    diff = list(difflib.unified_diff(orig_text, mod_text, fromfile=original_path, tofile=modified_path, lineterm=""))

    redline_markdown = (
        f"# SWEETYAI LEGAL REDLINE & TRACKED CHANGES REPORT\n"
        f"**Original Document:** {original_path}\n"
        f"**Modified Document:** {modified_path}\n"
        f"**Generated:** {today}\n\n"
        f"---\n\n"
        f"## I. TRACKED CHANGES SUMMARY (UNIFIED DIFF)\n"
        f"```diff\n"
    )

    for line in diff:
        redline_markdown += f"{line}\n"

    redline_markdown += (
        f"```\n\n"
        f"## II. INSTRUCTIONS FOR MICROSOFT WORD EXPORT\n"
        f"1. Open Microsoft Word.\n"
        f"2. Go to **Review -> Compare** to view side-by-side tracked changes, or paste this unified diff into your document where insertions are highlighted in green and deletions in strikethrough red.\n"
    )

    slug_orig = os.path.basename(original_path).rsplit(".", 1)[0]
    slug_mod = os.path.basename(modified_path).rsplit(".", 1)[0]
    out_path = os.path.join(REDLINE_DIR, f"redline_{slug_orig}_vs_{slug_mod}.md")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(redline_markdown)

    print("\n" + redline_markdown[:1500] + "\n... [truncated for console display] ...\n")
    print("=========================================================================")
    print(f"[Success] Redline Comparison Report saved to -> '{out_path}'")
    print("=========================================================================\n")
