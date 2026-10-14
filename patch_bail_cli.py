with open("sweety.py", "r", encoding="utf-8") as f:
    code = f.read().replace("\u00a0", " ")

bail_hook = """    if _cmd == "bail" or (_cmd == "legal" and _sub == "bail"):
        from bail_petition_generator import handle_bail_cli
        _args = _sys.argv[2:] if _cmd == "bail" else _sys.argv[3:]
        handle_bail_cli(_args)
        _sys.exit(0)
"""

if "from bail_petition_generator import handle_bail_cli" not in code:
    code = code.replace(
        "# --- SWEETYAI UNIFIED FAST-PATH ROUTER (END) ---",
        bail_hook + "# --- SWEETYAI UNIFIED FAST-PATH ROUTER (END) ---",
    )
    with open("sweety.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("[Success] 'sweety legal bail' wired into sweety.py!")
