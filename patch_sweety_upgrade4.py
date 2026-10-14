with open("sweety.py", "r") as f:
    code = f.read()

target_block = '''    # sweety legal brief
    b_parser = legal_subparsers.add_parser(
        "brief", help="Generate an automated IRAC legal memorandum"
    )
    b_parser.add_argument("topic", type=str, help="The legal question or research topic")'''

addition_block = '''

    # sweety legal audit
    a_parser = legal_subparsers.add_parser(
        "audit", help="Forensic FIR & Charge Sheet Defect Auditor (BNS/BNSS/BSA & SC Precedents)"
    )
    a_parser.add_argument("target", type=str, help="Path to FIR file or inline FIR allegation text")
    a_parser.add_argument("--offence-date", default=None, help="Date of alleged offence (YYYY-MM-DD) to check 01-07-2024 BNS/IPC cutoff")

    # sweety legal calc
    c_parser = legal_subparsers.add_parser(
        "calc", help="Calculate 60/90-day Default Bail (Sec 187 BNSS) & Cognizance Limitation (Sec 514 BNSS)"
    )
    c_parser.add_argument("--remand-date", required=True, help="Date of first judicial/magistrate remand (YYYY-MM-DD)")
    c_parser.add_argument("--max-years", type=float, required=True, help="Maximum imprisonment years prescribed for the offence")'''

if '"audit"' not in code:
    code = code.replace(target_block, target_block + addition_block)

dispatch_target = '''    elif args.legal_command == "brief":
        generate_legal_brief(args.topic)'''

dispatch_addition = '''
    elif args.legal_command == "audit":
        from litigation_auditor import audit_fir_or_chargesheet
        audit_fir_or_chargesheet(args.target, args.offence_date)
    elif args.legal_command == "calc":
        from litigation_auditor import calculate_remand_and_limitation
        calculate_remand_and_limitation(args.remand_date, args.max_years)'''

if 'args.legal_command == "audit"' not in code:
    code = code.replace(dispatch_target, dispatch_target + dispatch_addition)

with open("sweety.py", "w") as f:
    f.write(code)
print("[Upgrade 4 Installed] 'sweety legal audit' and 'sweety legal calc' are now active!")
