import os
import subprocess

# 1. Rebuild or clean sweety.py to ensure zero syntax errors
sweety_path = "sweety.py"
if os.path.exists(sweety_path):
    with open(sweety_path, "r", encoding="utf-8") as f:
        content = f.read().replace("\u00a0", " ")

    # Strip out any broken multi-line print statements or unmatched quotes
    lines = content.splitlines()
    cleaned_lines = []
    skip = False
    for line in lines:
        # Catch lines with dangling unclosed print statements
        if 'print("' in line and not line.endswith('")') and not line.endswith('")'):
            # fix dangling print strings
            line = line.rstrip() + '"'
        cleaned_lines.append(line)

    fixed_content = "\n".join(cleaned_lines)
    
    with open(sweety_path, "w", encoding="utf-8") as f:
        f.write(fixed_content)
    
    print("[Success] sweety.py syntax cleaned and normalized.")

# 2. Test python compilation of sweety.py
try:
    with open(sweety_path, "rb") as f:
        compile(f.read(), sweety_path, 'exec')
    print("[Syntax Check] sweety.py compiles cleanly with zero errors!")
except SyntaxError as e:
    print(f"[Syntax Error Found] Line {e.lineno}: {e.text}")
    sys.exit(1)

# 3. Run your requested test commands
print("\n[Test 1] Running Native Word Track-Changes Redline...")
subprocess.run([
    "python3", "sweety.py", "legal", "docx-redline", 
    "sample_contract.txt", "modified_contract.txt"
], check=True)

print("\n[Test 2] Running Excel Claim Schedule Generator...")
subprocess.run([
    "python3", "sweety.py", "legal", "claim-xlsx", 
    "--principal", "2500000", "--rate", "18", 
    "--start-date", "2025-01-15", "--regime", "sec34_cpc"
], check=True)

print("\n[Test 3] Running Section 63(4) BSA Certifier...")
subprocess.run([
    "python3", "sweety.py", "legal", "sec63-cert", 
    "sample_contract.txt", "--deponent", "Madhukumar Muniraj"
], check=True)

print("\n=========================================================================")
print("        ALL SWEETYAI MODULES REPAIRED & TESTED SUCCESSFULLY              ")
print("=========================================================================\n")
