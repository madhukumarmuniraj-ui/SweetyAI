with open("sweety.py", "r") as f:
    code = f.read()

pipeline_handler = '''
def handle_pipeline_cli(argv):
    p_parser = argparse.ArgumentParser(
        prog="sweety pipeline",
        description="Automated Operational Tracks: SEO keyword analysis, lead generation, and content pipelines.",
    )
    p_parser.add_argument(
        "niche",
        nargs="+",
        help="Target legal/operational topic or practice area",
    )
    args = p_parser.parse_args(argv)
    niche_str = " ".join(args.niche)
    from pipeline_agent import run_operational_pipeline
    run_operational_pipeline(niche_str)
'''

if "def handle_pipeline_cli" not in code:
    code = code.replace("def main():", pipeline_handler + "\n\ndef main():")

if 'sys.argv[1] == "pipeline"' not in code:
    target = 'if sys.argv[1] == "legal":\n            handle_legal_cli(sys.argv[2:])\n            return'
    replacement = target + '\n        elif sys.argv[1] == "pipeline":\n            handle_pipeline_cli(sys.argv[2:])\n            return'
    code = code.replace(target, replacement)

with open("sweety.py", "w") as f:
    f.write(code)
print("[Stage 5 Installed] 'sweety pipeline' is now active!")
