with open("sweety.py", "r") as f:
    code = f.read()

draft_subparser_snippet = '''    # sweety legal brief
    b_parser = legal_subparsers.add_parser(
        "brief", help="Generate an automated IRAC legal memorandum"
    )
    b_parser.add_argument("topic", type=str, help="The legal question or research topic")'''

new_draft_subparser = draft_subparser_snippet + '''

    # sweety legal draft
    d_parser = legal_subparsers.add_parser(
        "draft", help="Draft court-ready High Court / Sessions Court pleadings (BNSS/BNS/BSA)"
    )
    d_parser.add_argument(
        "--type",
        choices=["quashing", "anticipatory-bail", "regular-bail"],
        default="quashing",
        help="Type of pleading: quashing (Sec 528 BNSS / 482 CrPC), anticipatory-bail (Sec 482 BNSS / 438 CrPC), or regular-bail (Sec 483 BNSS / 439 CrPC)",
    )
    d_parser.add_argument(
        "facts",
        nargs="+",
        help="Brief factual matrix or case scenario for the petition",
    )'''

if '"draft"' not in code:
    code = code.replace(draft_subparser_snippet, new_draft_subparser)

old_legal_dispatch = '''    elif args.legal_command == "brief":
        generate_legal_brief(args.topic)'''

new_legal_dispatch = old_legal_dispatch + '''
    elif args.legal_command == "draft":
        from pleading_drafter import draft_pleading
        draft_pleading(args.type, " ".join(args.facts))'''

if 'args.legal_command == "draft"' not in code:
    code = code.replace(old_legal_dispatch, new_legal_dispatch)

with open("sweety.py", "w") as f:
    f.write(code)
print("[Upgrade 3 Installed] 'sweety legal draft' is now active!")
