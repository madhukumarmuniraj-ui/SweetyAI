with open("sweety.py", "r") as f:
    code = f.read()

target_block = '''    # sweety legal brief
    b_parser = legal_subparsers.add_parser(
        "brief", help="Generate an automated IRAC legal memorandum"
    )
    b_parser.add_argument("topic", type=str, help="The legal question or research topic")'''

addition_block = '''

    # sweety legal trial
    t_parser = legal_subparsers.add_parser(
        "trial", help="Trial Advocacy Engine: Cross-Examination (Sec 148 BSA), Sec 63(4) BSA Certificate, & Sec 138 NI Act"
    )
    t_parser.add_argument(
        "--mode",
        choices=["cross", "cert-63bsa", "ni138"],
        required=True,
        help="Mode: 'cross' (Cross-Examination), 'cert-63bsa' (Electronic Evidence Certificate), or 'ni138' (Cheque Bounce Timeline & Notice)",
    )
    t_parser.add_argument("--witness", choices=["io", "panch", "complainant"], default="io", help="Witness type for cross-examination")
    t_parser.add_argument("--facts", default="Alleged offence under BNS/IPC", help="Case facts or electronic record description")
    t_parser.add_argument("--device", default="Apple iPhone / Dell Server Terminal", help="Device description for Sec 63(4) BSA certificate")
    t_parser.add_argument("--dishonour-date", default="2026-09-01", help="Cheque dishonour memo date (YYYY-MM-DD) for NI Act 138")
    t_parser.add_argument("--served-date", default="2026-09-12", help="Notice service date (YYYY-MM-DD) for NI Act 138")'''

if '"trial"' not in code:
    code = code.replace(target_block, target_block + addition_block)

dispatch_target = '''    elif args.legal_command == "brief":
        generate_legal_brief(args.topic)'''

dispatch_addition = '''
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
            calculate_ni_act_138(args.dishonour_date, args.served_date)'''

if 'args.legal_command == "trial"' not in code:
    code = code.replace(dispatch_target, dispatch_target + dispatch_addition)

with open("sweety.py", "w") as f:
    f.write(code)
print("[Upgrade 5 Installed] 'sweety legal trial' is now active!")
