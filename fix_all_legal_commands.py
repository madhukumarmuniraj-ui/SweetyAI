with open("sweety.py", "r") as f:
    code = f.read()

# Re-define handle_legal_cli cleanly with all subcommands included
clean_legal_cli = '''
def handle_legal_cli(argv):
    legal_parser = argparse.ArgumentParser(
        prog="sweety legal",
        description="Sweety Legal AI RAG, Brief, Draft, Audit & Trial commands",
    )
    legal_subparsers = legal_parser.add_subparsers(dest="legal_command", required=True)

    # 1. query
    q_parser = legal_subparsers.add_parser("query", help="Query the legal RAG database")
    q_parser.add_argument("text", type=str, help="The legal question or prompt")

    # 2. ingest
    i_parser = legal_subparsers.add_parser("ingest", help="Ingest legal document into vector store")
    i_parser.add_argument("--doc-id", required=True, help="Unique document ID")
    i_parser.add_argument("--text", required=True, help="Body text/content")
    i_parser.add_argument("--source", required=True, help="Source citation")

    # 3. brief
    b_parser = legal_subparsers.add_parser("brief", help="Generate an automated IRAC legal memorandum")
    b_parser.add_argument("topic", type=str, help="The legal question or research topic")

    # 4. draft
    d_parser = legal_subparsers.add_parser("draft", help="Draft court-ready High Court / Sessions Court pleadings (BNSS/BNS/BSA)")
    d_parser.add_argument("--type", choices=["quashing", "anticipatory-bail", "regular-bail"], default="quashing", help="Pleading type")
    d_parser.add_argument("facts", nargs="+", help="Brief factual matrix")

    # 5. audit
    a_parser = legal_subparsers.add_parser("audit", help="Forensic FIR & Charge Sheet Defect Auditor")
    a_parser.add_argument("target", type=str, help="Path to FIR file or text")
    a_parser.add_argument("--offence-date", default=None, help="Offence date (YYYY-MM-DD)")

    # 6. calc
    c_parser = legal_subparsers.add_parser("calc", help="Calculate Default Bail & Limitation (Sec 187/514 BNSS)")
    c_parser.add_argument("--remand-date", required=True, help="First remand date (YYYY-MM-DD)")
    c_parser.add_argument("--max-years", type=float, required=True, help="Max punishment years")

    # 7. trial
    t_parser = legal_subparsers.add_parser("trial", help="Trial Advocacy: Cross-Exam, Sec 63(4) BSA Cert, & NI Act 138")
    t_parser.add_argument("--mode", choices=["cross", "cert-63bsa", "ni138"], required=True, help="Trial mode")
    t_parser.add_argument("--witness", choices=["io", "panch", "complainant"], default="io", help="Witness type")
    t_parser.add_argument("--facts", default="Alleged offence", help="Facts or electronic record desc")
    t_parser.add_argument("--device", default="Device Terminal", help="Device for BSA cert")
    t_parser.add_argument("--dishonour-date", default="2026-09-01", help="Cheque dishonour date")
    t_parser.add_argument("--served-date", default="2026-09-12", help="Notice service date")

    args = legal_parser.parse_args(argv)

    if args.legal_command == "query":
        query_rag(args.text)
    elif args.legal_command == "ingest":
        ingest_doc(args.doc_id, args.text, args.source)
    elif args.legal_command == "brief":
        generate_legal_brief(args.topic)
    elif args.legal_command == "draft":
        from pleading_drafter import draft_pleading
        draft_pleading(args.type, " ".join(args.facts))
    elif args.legal_command == "audit":
        from litigation_auditor import audit_fir_or_chargesheet
        audit_fir_or_chargesheet(args.target, args.offence_date)
    elif args.legal_command == "calc":
        from litigation_auditor import calculate_remand_and_limitation
        calculate_remand_and_limitation(args.remand_date, args.max_years)
    elif args.legal_command == "trial":
        from trial_advocacy_engine import (
            generate_cross_examination,
            generate_section_63_bsa_certificate,
            calculate_ni_act_138,
        )
        if args.mode == "cross":
            generate_cross_examination(args.witness, args.facts)
        elif args.mode == "cert-63bsa":
            generate_section_63_bsa_certificate(args.device, args.facts)
        elif args.mode == "ni138":
            calculate_ni_act_138(args.dishonour_date, args.served_date)
'''

# Replace old handle_legal_cli definition
start_idx = code.find("def handle_legal_cli(")
if start_idx != -1:
    # Find next function definition or end of file
    next_func_idx = code.find("\ndef ", start_idx + 1)
    if next_func_idx != -1:
        code = code[:start_idx] + clean_legal_cli + code[next_func_idx:]
    else:
        code = code[:start_idx] + clean_legal_cli
else:
    # Append if not found
    code += "\n" + clean_legal_cli

with open("sweety.py", "w") as f:
    f.write(code)

print("[Success] All legal commands (query, ingest, brief, draft, audit, calc, trial) successfully unified in sweety.py!")
