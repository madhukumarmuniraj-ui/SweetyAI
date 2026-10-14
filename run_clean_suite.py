import os
import sys
import time
import subprocess

# 1. Clean script builder function
def write_clean_file(filename, content):
    # Strip any potential non-breaking spaces or weird encodings
    cleaned = content.replace("\u00a0", " ")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(cleaned)

# 2. Write sandbox_guard.py
write_clean_file("sandbox_guard.py", '''
import os
import sys
import builtins

ALLOWED_HOME = os.path.realpath(os.path.expanduser("~"))
_orig_open = builtins.open
_orig_remove = os.remove
_orig_unlink = os.unlink
_orig_rename = os.rename
_orig_replace = os.replace
_orig_makedirs = os.makedirs
_orig_mkdir = os.mkdir
_orig_chmod = os.chmod

WRITE_MODES = ("w", "a", "x", "+")
SAFE_SYSTEM_READ_PREFIXES = (
    "/usr", "/lib", "/lib64", "/etc/localtime", "/etc/TZ", 
    "/etc/resolv.conf", "/etc/hosts", "/etc/ssl", "/etc/ca-certificates",
    "/proc/self", "/proc/meminfo", "/proc/cpuinfo", "/dev/null", "/dev/urandom", "/dev/random"
)

def _is_inside_home(path):
    if isinstance(path, int): return True
    try:
        real_target = os.path.realpath(os.path.expanduser(str(path)))
        return real_target == ALLOWED_HOME or real_target.startswith(ALLOWED_HOME + os.sep)
    except Exception:
        return False

def _verify_access(path, is_write=False, operation="access"):
    if isinstance(path, int) or _is_inside_home(path): return
    real_target = os.path.realpath(os.path.expanduser(str(path)))
    if is_write:
        raise PermissionError(f"[SweetyAI Sandbox Violation] Write/Modify '{operation}' BLOCKED on '{real_target}'. Restricted to '{ALLOWED_HOME}'.")
    if not any(real_target.startswith(p) for p in SAFE_SYSTEM_READ_PREFIXES):
        raise PermissionError(f"[SweetyAI Sandbox Violation] Read '{operation}' BLOCKED on '{real_target}'. Restricted to '{ALLOWED_HOME}'.")

def activate_home_sandbox():
    if os.geteuid() == 0:
        raise PermissionError("[SweetyAI Security] Running SweetyAI as root (sudo) is strictly prohibited.")
    builtins.open = lambda file, mode="r", *a, **kw: (_verify_access(file, is_write=any(m in mode for m in WRITE_MODES), operation=f"open({mode})"), _orig_open(file, mode, *a, **kw))[1]
    os.remove = lambda p, *a, **kw: (_verify_access(p, is_write=True, operation="os.remove"), _orig_remove(p, *a, **kw))[1]
    os.unlink = lambda p, *a, **kw: (_verify_access(p, is_write=True, operation="os.unlink"), _orig_unlink(p, *a, **kw))[1]
    os.rename = lambda s, d, *a, **kw: (_verify_access(s, is_write=True, operation="os.rename(src)"), _verify_access(d, is_write=True, operation="os.rename(dst)"), _orig_rename(s, d, *a, **kw))[2]
    os.replace = lambda s, d, *a, **kw: (_verify_access(s, is_write=True, operation="os.replace(src)"), _verify_access(d, is_write=True, operation="os.replace(dst)"), _orig_replace(s, d, *a, **kw))[2]
    os.makedirs = lambda n, *a, **kw: (_verify_access(n, is_write=True, operation="os.makedirs"), _orig_makedirs(n, *a, **kw))[1]
    os.mkdir = lambda p, *a, **kw: (_verify_access(p, is_write=True, operation="os.mkdir"), _orig_mkdir(p, *a, **kw))[1]
    os.chmod = lambda p, m, *a, **kw: (_verify_access(p, is_write=True, operation="os.chmod"), _orig_chmod(p, m, *a, **kw))[1]
''')

# 3. Ensure sandbox guard header is active in sweety.py
if os.path.exists("sweety.py"):
    with open("sweety.py", "r", encoding="utf-8") as f:
        code = f.read().replace("\u00a0", " ")
    header = "# --- SWEETYAI HOME-DIRECTORY SANDBOX ENFORCEMENT ---\nfrom sandbox_guard import activate_home_sandbox as _activate_home_sandbox\n_activate_home_sandbox()\n# ---------------------------------------------------\n"
    if "from sandbox_guard import activate_home_sandbox" not in code:
        code = header + "\n" + code
        write_clean_file("sweety.py", code)

print("[Success] Sandbox guard initialized and wired cleanly!")
print("Run `python3 sweety.py --help` or test your legal workflows securely inside ~/madhukumarm.")
