with open("sweety.py", "r") as f:
    code = f.read()

devtools_handler = '''
def handle_devtools_cli(argv):
    dt_parser = argparse.ArgumentParser(
        prog="sweety devtools",
        description="Headless Chrome DevTools Agent: debug layout, check network constraints, and auto-patch code.",
    )
    dt_parser.add_argument("target", type=str, help="Target URL or local HTML file (e.g., index.html)")
    dt_parser.add_argument("--patch", action="store_true", help="Autonomously patch detected layout/DOM flaws")
    args = dt_parser.parse_args(argv)
    from devtools_agent import audit_and_patch
    audit_and_patch(args.target, auto_patch=args.patch)
'''

if "def handle_devtools_cli" not in code:
    code = code.replace("def main():", devtools_handler + "\n\ndef main():")

old_router = '''    # Route 'sweety legal ...' directly to the legal sub-CLI
    if len(sys.argv) > 1 and sys.argv[1] == "legal":
        handle_legal_cli(sys.argv[2:])
        return'''

new_router = '''    import shlex
    # Unpack if shell wrapper passed all arguments as a single quoted string
    if len(sys.argv) == 2 and " " in sys.argv[1]:
        first_word = sys.argv[1].strip().split()[0]
        if first_word in ("legal", "devtools", "vision", "daemon", "orchestrate", "pipeline", "swarm"):
            sys.argv = [sys.argv[0]] + shlex.split(sys.argv[1])

    if len(sys.argv) > 1:
        if sys.argv[1] == "legal":
            handle_legal_cli(sys.argv[2:])
            return
        elif sys.argv[1] == "devtools":
            handle_devtools_cli(sys.argv[2:])
            return'''

if old_router in code:
    code = code.replace(old_router, new_router)
with open("sweety.py", "w") as f:
    f.write(code)
print("[Stage 1 Installed] 'sweety devtools' is now active!")
