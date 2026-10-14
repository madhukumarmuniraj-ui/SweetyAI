import os
from sandbox_guard import activate_home_sandbox, ALLOWED_HOME

# Wire into sweety.py before activating test
if os.path.exists("sweety.py"):
    with open("sweety.py", "r", encoding="utf-8") as sf:
        code = sf.read().replace("\u00a0", " ")
    header = "# --- SWEETYAI HOME-DIRECTORY SANDBOX ENFORCEMENT ---\nfrom sandbox_guard import activate_home_sandbox as _activate_home_sandbox\n_activate_home_sandbox()\n# ---------------------------------------------------\n"
    if "from sandbox_guard import activate_home_sandbox" not in code:
        with open("sweety.py", "w", encoding="utf-8") as sf:
            sf.write(header + "\n" + code)

activate_home_sandbox()

print("\n=== SweetyAI Home-Directory Permission & Root-Block Verification ===")
print(f"Authorized Sandbox Directory : {ALLOWED_HOME}")

# Test 1: Read, Write, Chmod, and Delete inside /home/madhukumarm/SweetyAI
test_file = os.path.expanduser("~/SweetyAI/.sandbox_write_test.tmp")
with open(test_file, "w") as f:
    f.write("SweetyAI read/write/modify test inside home directory.")
os.chmod(test_file, 0o644)
with open(test_file, "r") as f:
    data = f.read()
os.remove(test_file)
print(f"[PASS] Test 1 (Read/Write/Chmod/Delete in {ALLOWED_HOME}) : ALLOWED")

# Test 2: Attempt to write a file in Root (/) -> Must be BLOCKED
try:
    with open("/root_escape_test.txt", "w") as f:
        f.write("blocked")
    print("[FAIL] Test 2 (Write to /) : Should have been blocked!")
except PermissionError as e:
    print(f"[PASS] Test 2 (Write to /root_escape_test.txt) : BLOCKED -> {e}")

# Test 3: Attempt to read sensitive root file (/etc/passwd) -> Must be BLOCKED
try:
    with open("/etc/passwd", "r") as f:
        _ = f.read()
    print("[FAIL] Test 3 (Read /etc/passwd) : Should have been blocked!")
except PermissionError as e:
    print(f"[PASS] Test 3 (Read /etc/passwd outside ~)     : BLOCKED -> {e}")

# Test 4: Attempt Path Traversal (~/SweetyAI/../../../tmp/escape.txt) -> Must be BLOCKED
try:
    with open(os.path.expanduser("~/SweetyAI/../../../tmp/escape.txt"), "w") as f:
        f.write("blocked")
    print("[FAIL] Test 4 (Path Traversal ../) : Should have been blocked!")
except PermissionError as e:
    print(f"[PASS] Test 4 (Path Traversal ../../../tmp)    : BLOCKED -> {e}")

print("====================================================================\n")
