with open("sweety.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("\u00a0", " ")

chronology_intercept = """import sys
if len(sys.argv) > 1 and sys.argv[1] in ("chronology", "list-of-dates"):
    from chronology_extractor import handle_chronology_cli
    handle_chronology_cli(sys.argv[2:])
    sys.exit(0)
if len(sys.argv) > 2 and sys.argv[1] == "legal" and sys.argv[2] in ("chronology", "list-of-dates"):
    from chronology_extractor import handle_chronology_cli
    handle_chronology_cli(sys.argv[3:])
    sys.exit(0)
"""

if "from chronology_extractor import handle_chronology_cli" not in code:
    code = chronology_intercept + "\n" + code

with open("sweety.py", "w", encoding="utf-8") as f:
    f.write(code)

print("[Success] 'sweety legal chronology' wired at the top of sweety.py!")
