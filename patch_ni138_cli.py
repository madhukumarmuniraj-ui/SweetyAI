with open("sweety.py", "r", encoding="utf-8") as f:
    code = f.read().replace("\u00a0", " ")

ni138_hook = """    if _cmd == "ni138" or (_cmd == "legal" and _sub == "ni138"):
        from ni138_engine import handle_ni138_cli
        _args = _sys.argv[2:] if _cmd == "ni138" else _sys.argv[3:]
        handle_ni138_cli(_args)
        _sys.exit(0)
"""

if "from ni138_engine import handle_ni138_cli" not in code:
    code = code.replace(
        "# --- SWEETYAI UNIFIED FAST-PATH ROUTER (END) ---",
        ni138_hook + "# --- SWEETYAI UNIFIED FAST-PATH ROUTER (END) ---",
    )
    with open("sweety.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("[Success] 'sweety legal ni138' wired into sweety.py!")
