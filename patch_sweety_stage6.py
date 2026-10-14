with open("sweety.py", "r") as f:
    code = f.read()

swarm_handler = '''
def handle_swarm_cli(argv):
    s_parser = argparse.ArgumentParser(
        prog="sweety swarm",
        description="Multi-Agent CLI & SDK Orchestrator (Statutory + Precedent + Drafting + Verifier Agents).",
    )
    s_parser.add_argument(
        "objective",
        nargs="+",
        help="Complex multi-agent legal or operational objective",
    )
    args = s_parser.parse_args(argv)
    obj_str = " ".join(args.objective)
    from sweety_sdk import SwarmOrchestrator
    SwarmOrchestrator().run_swarm(obj_str)
'''

if "def handle_swarm_cli" not in code:
    code = code.replace("def main():", swarm_handler + "\n\ndef main():")

if 'sys.argv[1] == "swarm"' not in code:
    target = 'if sys.argv[1] == "legal":\n            handle_legal_cli(sys.argv[2:])\n            return'
    replacement = target + '\n        elif sys.argv[1] == "swarm":\n            handle_swarm_cli(sys.argv[2:])\n            return'
    code = code.replace(target, replacement)

with open("sweety.py", "w") as f:
    f.write(code)
print("[Stage 6 Installed] 'sweety swarm' and 'sweety_sdk.py' are now active!")
