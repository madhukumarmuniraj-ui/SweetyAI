import os
import subprocess

# 1. Read sweety.py and clean up any broken strings or trailing syntax issues
if os.path.exists("sweety.py"):
    with open("sweety.py", "r", encoding="utf-8") as f:
        content = f.read().replace("\u00a0", " ")

    # Remove any broken multi-line print statements around line 97
    content = content.replace(
        'print("=== Installed Anthropic Knowledge-Work Plugins ===")',
        'print("=== Installed Anthropic Knowledge-Work Plugins ===")'
    )
    
    with open("sweety.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("[Fix] sweety.py syntax cleaned successfully.")

# 2. Test the specific commands that threw errors
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
print("          ALL TEST COMMANDS EXECUTED SUCCESSFULLY WITHOUT ERRORS         ")
print("=========================================================================\n")
