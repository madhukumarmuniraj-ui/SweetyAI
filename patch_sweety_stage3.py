with open("sweety.py", "r") as f:
    code = f.read()

daemon_handler = '''
def handle_daemon_cli(argv):
    d_parser = argparse.ArgumentParser(
        prog="sweety daemon",
        description="24/7 Always-On Proactive Background Agent Suite.",
    )
    d_parser.add_argument(
        "action",
        nargs="?",
        default="status",
        choices=["start", "stop", "status", "run-once"],
        help="Action: start, stop, status, or run-once",
    )
    args = d_parser.parse_args(argv)
    from daemon_agent import start_daemon, stop_daemon, status_daemon, run_single_cycle
    if args.action == "start":
        start_daemon()
    elif args.action == "stop":
        stop_daemon()
    elif args.action == "run-once":
        run_single_cycle(verbose=True)
    else:
        status_daemon()
'''

if "def handle_daemon_cli" not in code:
    code = code.replace("def main():", daemon_handler + "\n\ndef main():")

if 'sys.argv[1] == "daemon"' not in code:
    target = 'if sys.argv[1] == "legal":\n            handle_legal_cli(sys.argv[2:])\n            return'
    replacement = target + '\n        elif sys.argv[1] == "daemon":\n            handle_daemon_cli(sys.argv[2:])\n            return'
    code = code.replace(target, replacement)

with open("sweety.py", "w") as f:
    f.write(code)
print("[Stage 3 Installed] 'sweety daemon' is now active!")
