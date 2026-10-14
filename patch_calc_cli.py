with open("sweety.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("\u00a0", " ")

calc_intercept = """import sys
if len(sys.argv) > 1 and sys.argv[1] in ("calc-fees", "calc"):
    from court_fee_calculator import handle_calc_cli
    handle_calc_cli(sys.argv[2:])
    sys.exit(0)
if len(sys.argv) > 2 and sys.argv[1] == "legal" and sys.argv[2] in ("calc-fees", "calc"):
    from court_fee_calculator import handle_calc_cli
    handle_calc_cli(sys.argv[3:])
    sys.exit(0)
"""

if "from court_fee_calculator import handle_calc_cli" not in code:
    code = calc_intercept + "\n" + code

with open("sweety.py", "w", encoding="utf-8") as f:
    f.write(code)

print("[Success] 'sweety calc-fees' and 'sweety legal calc-fees' wired into sweety.py!")
