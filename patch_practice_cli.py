with open("sweety.py", "r") as f:
    code = f.read()

practice_cli_def = '''
def handle_practice_cli(argv):
    p_parser = argparse.ArgumentParser(
        prog="sweety practice",
        description="Enterprise Practice Packages (Corporate, Litigation, Employment, Privacy, Criminal).",
    )
    p_parser.add_argument("domain", nargs="?", default="list", help="Domain key (corporate, litigation, employment, privacy, criminal) or 'list'")
    args = p_parser.parse_args(argv)
    from practice_packages import list_practice_packages, run_practice_package
    if args.domain == "list":
        list_practice_packages()
    else:
        run_practice_package(args.domain)
'''

if "def handle_practice_cli" not in code:
    code = code.replace("def main():", practice_cli_def + "\n\ndef main():")

if 'sys.argv[1] == "practice"' not in code:
    target = 'elif sys.argv[1] == "skill":\n            handle_skill_cli(sys.argv[2:])\n            return'
    replacement = target + '\n        elif sys.argv[1] == "practice":\n            handle_practice_cli(sys.argv[2:])\n            return'
    code = code.replace(target, replacement)

with open("sweety.py", "w") as f:
    f.write(code)

print("[Success] 'sweety practice' integrated into sweety.py!")
