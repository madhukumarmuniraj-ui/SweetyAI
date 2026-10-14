with open("sweety.py", "r") as f:
    code = f.read()

subparser_snippet = '''
    # 11. redline (Markdown Redline & Tracked Changes)
    rl_parser = legal_subparsers.add_parser("redline", help="Generate unified diff redline between two legal documents")
    rl_parser.add_argument("original", type=str, help="Path to original document")
    rl_parser.add_argument("modified", type=str, help="Path to modified document")
'''

dispatch_snippet = '''
    elif args.legal_command == "redline":
        from redline_generator import generate_redline
        generate_redline(args.original, args.modified)
'''

if 'legal_subparsers.add_parser("redline"' not in code:
    code = code.replace(
        'args = legal_parser.parse_args(argv)',
        subparser_snippet + '\n    args = legal_parser.parse_args(argv)'
    )

if 'args.legal_command == "redline"' not in code:
    code = code.replace(
        'elif args.legal_command == "verify-citations":',
        'elif args.legal_command == "redline":\n        from redline_generator import generate_redline\n        generate_redline(args.original, args.modified)\n    elif args.legal_command == "verify-citations":'
    )

with open("sweety.py", "w") as f:
    f.write(code)

print("[Success] 'sweety legal redline' integrated into sweety.py!")
