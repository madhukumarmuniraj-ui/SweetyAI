with open("sweety.py", "r") as f:
    code = f.read()

subparser_snippet = '''
    # 12. parallel (Parallel Precedent & Counter-Argument Finder)
    p_parser = legal_subparsers.add_parser("parallel", help="Find parallel precedents and generate counter-argument analysis")
    p_parser.add_argument("proposition", type=str, help="Legal proposition or argument to analyze")
'''

dispatch_snippet = '''
    elif args.legal_command == "parallel":
        from parallel_precedent import find_parallel_precedents
        find_parallel_precedents(args.proposition)
'''

if 'legal_subparsers.add_parser("parallel"' not in code:
    code = code.replace(
        'args = legal_parser.parse_args(argv)',
        subparser_snippet + '\n    args = legal_parser.parse_args(argv)'
    )

if 'args.legal_command == "parallel"' not in code:
    code = code.replace(
        'elif args.legal_command == "verify-citations":',
        'elif args.legal_command == "parallel":\n        from parallel_precedent import find_parallel_precedents\n        find_parallel_precedents(args.proposition)\n    elif args.legal_command == "verify-citations":'
    )

with open("sweety.py", "w") as f:
    f.write(code)

print("[Success] 'sweety legal parallel' integrated into sweety.py!")
