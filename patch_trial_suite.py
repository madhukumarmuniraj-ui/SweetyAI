with open("sweety.py", "r", encoding="utf-8") as f:
    code = f.read().replace("\u00a0", " ")

suite_hook = """    if _cmd in ("sec63-cert", "custody-calc", "cross-exam") or (_cmd == "legal" and _sub in ("sec63-cert", "custody-calc", "cross-exam")):
        from trial_and_evidence_suite import handle_suite_cli
        _target_cmd = _cmd if _cmd in ("sec63-cert", "custody-calc", "cross-exam") else _sub
        _args = _sys.argv[2:] if _cmd in ("sec63-cert", "custody-calc", "cross-exam") else _sys.argv[3:]
        handle_suite_cli(_target_cmd, _args)
        _sys.exit(0)
"""

if "from trial_and_evidence_suite import handle_suite_cli" not in code:
    code = code.replace(
        "# --- SWEETYAI UNIFIED FAST-PATH ROUTER (END) ---",
        suite_hook + "# --- SWEETYAI UNIFIED FAST-PATH ROUTER (END) ---",
    )
    with open("sweety.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("[Success] 'sec63-cert', 'custody-calc', and 'cross-exam' wired into sweety.py!")
