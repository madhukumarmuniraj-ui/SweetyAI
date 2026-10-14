with open("sweety.py", "r", encoding="utf-8") as f:
    code = f.read()

hook = """
        # Module 19: Karnataka Stamp Duty & Impounding Calculator
        if _cmd == "stamp-duty" or (_cmd == "legal" and _sub == "stamp-duty"):
            from stamp_duty_calculator import handle_stamp_cli
            _args = _sys.argv[2:] if _cmd == "stamp-duty" else _sys.argv[3:]
            handle_stamp_cli(_args)
            _sys.exit(0)
"""

if "from stamp_duty_calculator import handle_stamp_cli" not in code:
    code = code.replace("if _cmd in ("docx-export",", hook + "\n        if _cmd in ("docx-export",")
    with open("sweety.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("[Success] Stamp Duty Calculator wired into sweety.py!")
