with open("sweety.py", "r") as f:
    code = f.read()

export_cli_def = '''
def handle_export_cli(argv):
    e_parser = argparse.ArgumentParser(
        prog="sweety export",
        description="Export legal briefs and reports into court-ready formatted documents.",
    )
    e_parser.add_argument("file", help="Path to markdown pleading, petition, or report")
    e_parser.add_argument("--format", choices=["html", "docx"], default="html", help="Target output format")
    args = e_parser.parse_args(argv)
    
    from document_exporter import export_document
    export_document(args.file, args.format)
'''

if "def handle_export_cli" not in code:
    code = code.replace("def main():", export_cli_def + "\n\ndef main():")

if 'sys.argv[1] == "export"' not in code:
    target = 'elif sys.argv[1] == "web":\n            handle_web_cli(sys.argv[2:])\n            return'
    replacement = target + '\n        elif sys.argv[1] == "export":\n            handle_export_cli(sys.argv[2:])\n            return'
    code = code.replace(target, replacement)

with open("sweety.py", "w") as f:
    f.write(code)

print("[Success] 'sweety export' command integrated into sweety.py!")
