with open("sweety.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("\u00a0", " ")

verify_intercept = """import sys
if len(sys.argv) > 1 and sys.argv[1] == "verify-citations":
    from citation_verifier import handle_verify_cli
    handle_verify_cli(sys.argv[2:])
    sys.exit(0)
if len(sys.argv) > 2 and sys.argv[1] == "legal" and sys.argv[2] == "verify-citations":
    from citation_verifier import handle_verify_cli
    handle_verify_cli(sys.argv[3:])
    sys.exit(0)
"""

if "from citation_verifier import handle_verify_cli" not in code:
    code = verify_intercept + "\n" + code

with open("sweety.py", "w", encoding="utf-8") as f:
    f.write(code)

print("[Success] 'sweety legal verify-citations --latest' wired at the top of sweety.py!")
