with open("sweety.py", "r") as f:
    code = f.read()

# Add new subparsers into handle_legal_cli and main dispatcher if not already present
new_subparsers_snippet = '''
    # 8. review (Contract Playbook Audit)
    r_parser = legal_subparsers.add_parser("review", help="Audit contract against firm negotiation playbook")
    r_parser.add_argument("contract", type=str, help="Path to contract file (.md/.txt)")
    r_parser.add_argument("--playbook", default=None, help="Path to firm playbook file")

    # 9. ingest-batch (Bulk E-Discovery)
    ib_parser = legal_subparsers.add_parser("ingest-batch", help="Bulk ingest e-discovery folder into vector store")
    ib_parser.add_argument("folder", type=str, help="Path to folder containing documents")
'''

new_dispatch_snippet = '''
    elif args.legal_command == "review":
        from contract_reviewer import review_contract
        review_contract(args.contract, args.playbook)
    elif args.legal_command == "ingest-batch":
        from batch_ingestor import batch_ingest
        batch_ingest(args.folder)
'''

if 'legal_subparsers.add_parser("review"' not in code:
    code = code.replace(
        'args = legal_parser.parse_args(argv)',
        new_subparsers_snippet + '\n    args = legal_parser.parse_args(argv)'
    )

if 'args.legal_command == "review"' not in code:
    code = code.replace(
        'elif args.legal_command == "trial":',
        'elif args.legal_command == "review":\n        from contract_reviewer import review_contract\n        review_contract(args.contract, args.playbook)\n    elif args.legal_command == "ingest-batch":\n        from batch_ingestor import batch_ingest\n        batch_ingest(args.folder)\n    elif args.legal_command == "trial":'
    )

# Add top-level 'skill' command routing
skill_cli_def = '''
def handle_skill_cli(argv):
    s_parser = argparse.ArgumentParser(
        prog="sweety skill",
        description="Custom Firm SOP & Writing Voice Skill Registry.",
    )
    s_parser.add_argument("action", choices=["create", "list"], help="Action: create or list")
    s_parser.add_argument("--name", default="Firm SOP", help="Skill name")
    s_parser.add_argument("--desc", default="Standard operating procedure", help="Description")
    s_parser.add_argument("--sops", default="Formal legal writing, structured headings, rigorous citations.", help="SOPs and writing voice rules")
    args = s_parser.parse_args(argv)
    from firm_skill_engine import create_firm_skill, list_firm_skills
    if args.action == "create":
        create_firm_skill(args.name, args.desc, args.sops)
    else:
        list_firm_skills()
'''

if "def handle_skill_cli" not in code:
    code = code.replace("def main():", skill_cli_def + "\n\ndef main():")

if 'sys.argv[1] == "skill"' not in code:
    target = 'elif sys.argv[1] == "swarm":\n            handle_swarm_cli(sys.argv[2:])\n            return'
    replacement = target + '\n        elif sys.argv[1] == "skill":\n            handle_skill_cli(sys.argv[2:])\n            return'
    code = code.replace(target, replacement)

with open("sweety.py", "w") as f:
    f.write(code)

print("[Success] All enterprise features (review, ingest-batch, skill) integrated into sweety.py!")
