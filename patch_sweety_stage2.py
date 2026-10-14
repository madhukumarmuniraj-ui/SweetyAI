with open("sweety.py", "r") as f:
    code = f.read()

vision_handler = '''
def handle_vision_cli(argv):
    v_parser = argparse.ArgumentParser(
        prog="sweety vision",
        description="Real-Time OS Screen Awareness: capture screen, inspect active window/docs, and answer questions.",
    )
    v_parser.add_argument(
        "question",
        nargs="*",
        default=["What am I currently viewing on my screen and what are the legal implications?"],
        help="Question about what you are actively viewing on screen",
    )
    args = v_parser.parse_args(argv)
    q = " ".join(args.question) if isinstance(args.question, list) else args.question
    from vision_agent import analyze_screen
    analyze_screen(q)
'''

if "def handle_vision_cli" not in code:
    code = code.replace("def main():", vision_handler + "\n\ndef main():")

if 'sys.argv[1] == "vision"' not in code:
    target = 'elif sys.argv[1] == "devtools":\n            handle_devtools_cli(sys.argv[2:])\n            return'
    replacement = target + '\n        elif sys.argv[1] == "vision":\n            handle_vision_cli(sys.argv[2:])\n            return'
    code = code.replace(target, replacement)

with open("sweety.py", "w") as f:
    f.write(code)
print("[Stage 2 Installed] 'sweety vision' is now active!")
