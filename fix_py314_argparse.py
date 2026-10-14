import glob
import re
import subprocess

# 1. Patch crl_appeal_engine.py and ibc_engine.py + scan all .py files for Python 3.14 argparse % compatibility
for py_file in glob.glob("*.py"):
    if py_file == "fix_py314_argparse.py":
        continue
    with open(py_file, "r", encoding="utf-8") as f:
        code = f.read().replace("\u00a0", " ").replace("\u200b", "")

    # Replace literal % inside help="..." strings with %% (unless already %% or %(...)s)
    def _escape_help_percent(match):
        prefix = match.group(1)
        help_text = match.group(2)
        quote = match.group(3)
        safe_help = re.sub(r"%(?!%|[\(\w])", "%%", help_text)
        return f"{prefix}{safe_help}{quote}"

    patched = re.sub(r'(help\s*=\s*["\'])([^"\']+)(["\'])', _escape_help_percent, code)
    if patched != code:
        with open(py_file, "w", encoding="utf-8") as f:
            f.write(patched)
        print(f"[Patched Python 3.14 argparse help] -> {py_file}")

print("\n=== [TEST 1] Module 20: Criminal Appeal & Sec. 430 BNSS Suspension of Sentence ===")
subprocess.run([
    "python3", "sweety.py", "legal", "crl-appeal",
    "--cc-no", "C.C. No. 18450/2024",
    "--judgment-date", "2026-09-25",
    "--fine", "1500000",
    "--sentence-months", "6",
    "--forum", "sessions"
], check=True)

print("\n=== [TEST 2] Module 21: IBC Sec. 8 Demand Notice (Form 3) & Sec. 9 NCLT Petition (Form 5) ===")
subprocess.run([
    "python3", "sweety.py", "legal", "ibc",
    "--principal", "11500000",
    "--rate", "18",
    "--default-date", "2025-11-10",
    "--invoice-no", "INV-BLR-2025-904"
], check=True)

print("\n=========================================================================")
print("   MODULES 20 & 21 VERIFIED ON PYTHON 3.14 WITH ZERO ARGPARSE ERRORS     ")
print("=========================================================================\n")
