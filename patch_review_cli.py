with open("sweety.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("\u00a0", " ")

review_intercept = """import sys
if len(sys.argv) > 1 and sys.argv[1] == "review":
    from contract_reviewer import handle_review_cli
    handle_review_cli(sys.argv[2:])
    sys.exit(0)
if len(sys.argv) > 2 and sys.argv[1] == "legal" and sys.argv[2] == "review":
    from contract_reviewer import handle_review_cli
    handle_review_cli(sys.argv[3:])
    sys.exit(0)
"""

if "from contract_reviewer import handle_review_cli" not in code:
    code = review_intercept + "\n" + code

with open("sweety.py", "w", encoding="utf-8") as f:
    f.write(code)

print("[Success] 'sweety legal review --latest' wired at the top of sweety.py!")
