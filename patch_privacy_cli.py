with open("sweety.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("\u00a0", " ")

privacy_intercept = """import sys
if len(sys.argv) > 1 and sys.argv[1] == "privacy-audit":
    from privacy_and_playbook_engine import handle_privacy_cli
    handle_privacy_cli(sys.argv[2:])
    sys.exit(0)
if len(sys.argv) > 2 and sys.argv[1] == "legal" and sys.argv[2] == "privacy-audit":
    from privacy_and_playbook_engine import handle_privacy_cli
    handle_privacy_cli(sys.argv[3:])
    sys.exit(0)
"""

if "from privacy_and_playbook_engine import handle_privacy_cli" not in code:
    code = privacy_intercept + "\n" + code

with open("sweety.py", "w", encoding="utf-8") as f:
    f.write(code)

print("[Success] 'sweety legal privacy-audit' wired into sweety.py!")
