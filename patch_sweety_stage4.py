with open("sweety.py", "r") as f:
    code = f.read()

orchestrate_handler = '''
def handle_orchestrate_cli(argv):
    o_parser = argparse.ArgumentParser(
        prog="sweety orchestrate",
        description="24/7 Multi-Step Cross-App Orchestrator (RAG + Docs + Gmail + Calendar/Logistics + Canva).",
    )
    o_parser.add_argument(
        "command",
        nargs="+",
        help="Broad natural language command to orchestrate across tools",
    )
    args = o_parser.parse_args(argv)
    cmd_str = " ".join(args.command)
    from orchestrator_agent import orchestrate_command
    orchestrate_command(cmd_str)
'''

if "def handle_orchestrate_cli" not in code:
    code = code.replace("def main():", orchestrate_handler + "\n\ndef main():")

if 'sys.argv[1] == "orchestrate"' not in code:
    target = 'if sys.argv[1] == "legal":\n            handle_legal_cli(sys.argv[2:])\n            return'
    replacement = target + '\n        elif sys.argv[1] == "orchestrate":\n            handle_orchestrate_cli(sys.argv[2:])\n            return'
    code = code.replace(target, replacement)

with open("sweety.py", "w") as f:
    f.write(code)
print("[Stage 4 Installed] 'sweety orchestrate' is now active!")
