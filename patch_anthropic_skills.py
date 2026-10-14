with open("sweety.py", "r", encoding="utf-8") as f:
    code = f.read().replace("\u00a0", " ")

hook = """    if _cmd in ("triage-nda", "risk-register") or (_cmd == "legal" and _sub in ("triage-nda", "risk-register")):
        from anthropic_legal_skills_suite import handle_anthropic_skills_cli
        _target_cmd = _cmd if _cmd in ("triage-nda", "risk-register") else _sub
        _args = _sys.argv[2:] if _cmd in ("triage-nda", "risk-register") else _sys.argv[3:]
        handle_anthropic_skills_cli(_target_cmd, _args)
        _sys.exit(0)
"""

if "from anthropic_legal_skills_suite import handle_anthropic_skills_cli" not in code:
    code = code.replace(
        "# --- SWEETYAI UNIFIED FAST-PATH ROUTER (END) ---",
        hook + "# --- SWEETYAI UNIFIED FAST-PATH ROUTER (END) ---",
    )
    with open("sweety.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("[Success] 'triage-nda' and 'risk-register' wired into sweety.py!")
