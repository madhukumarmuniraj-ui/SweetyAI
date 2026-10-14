with open("sweety.py", "r") as f:
    code = f.read()

subparser_snippet = '''
    # 10. verify-citations (Automated Citation Checker)
    vc_parser = legal_subparsers.add_parser("verify-citations", help="Verify case citations and statutory references against local vector corpus")
    vc_parser.add_argument("file", type=str, help="Path to legal brief or pleading file (.md/.txt)")
'''

dispatch_snippet = '''
    elif args.legal_command == "verify-citations":
        from citation_verifier import verify_file_citations
        verify_file_citations(args.file)
'''

if 'legal_subparsers.add_parser("verify-citations"' not in code:
    code = code.replace(
        'args = legal_parser.parse_args(argv)',
        subparser_snippet + '\n    args = legal_parser.parse_args(argv)'
    )

if 'args.legal_command == "verify-citations"' not in code:
    code = code.replace(
        'elif args.legal_command == "review":',
        'elif args.legal_command == "verify-citations":\n        from citation_verifier import verify_file_citations\n        verify_file_citations(args.file)\n    elif args.legal_command == "review":'
    )

with open("sweety.py", "w") as f:
    f.write(code)

print("[Success] 'sweety legal verify-citations' integrated into sweety.py!")
