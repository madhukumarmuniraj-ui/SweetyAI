import os
import subprocess

# 1. Ensure sweety.py has clean routing without quote conflicts
sweety_path = "sweety.py"
if os.path.exists(sweety_path):
    with open(sweety_path, "r", encoding="utf-8") as f:
        code = f.read().replace("\u00a0", " ")

    # Add the stamp-duty route cleanly if not already present
    if "stamp_duty_calculator" not in code:
        target = 'if _cmd in ("docx-export", "docx-redline", "claim-xlsx", "mcp-sync")'
        addition = '''        if _cmd == "stamp-duty" or (_cmd == "legal" and _sub == "stamp-duty"):
            from stamp_duty_calculator import handle_stamp_cli
            _args = _sys.argv[2:] if _cmd == "stamp-duty" else _sys.argv[3:]
            handle_stamp_cli(_args)
            _sys.exit(0)

'''
        if target in code:
            code = code.replace(target, addition + target)
            with open(sweety_path, "w", encoding="utf-8") as f:
                f.write(code)
            print("[Success] Stamp Duty Calculator route cleanly added to sweety.py!")
        else:
            print("[Note] Target route hook not found, checking existing routes...")

# 2. Run the Stamp Duty & Impounding Calculator test
print("\n[Test] Running Karnataka Stamp Duty & Impounding Calculator...")
subprocess.run([
    "python3", "sweety.py", "legal", "stamp-duty", 
    "--instrument", "conveyance_urban", 
    "--value", "7500000", 
    "--deficit", "100000"
], check=True)

print("\n=========================================================================")
print("          STAMP DUTY & IMPOUNDING MODULE FULLY OPERATIONAL               ")
print("=========================================================================\n")
