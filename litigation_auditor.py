import os
import re
import datetime

AUDIT_DIR = "fir_audit_reports"


def audit_fir_or_chargesheet(input_target, offence_date_str=None):
    os.makedirs(AUDIT_DIR, exist_ok=True)
    if os.path.exists(input_target):
        with open(input_target, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        source_label = f"File: {input_target}"
    else:
        text = input_target
        source_label = "Inline FIR / Fact Statement"

    text_lower = text.lower()
    defects = []
    citations = []

    # 1. Check 01-07-2024 IPC vs BNS Transition Cut-Off (Section 531 BNSS Savings Clause)
    cutoff_date = datetime.date(2024, 7, 1)
    if offence_date_str:
        try:
            off_date = datetime.datetime.strptime(offence_date_str, "%Y-%m-%d").date()
            if off_date < cutoff_date and ("bns" in text_lower or "bharatiya nyaya" in text_lower):
                defects.append(
                    f"[FATAL JURISDICTIONAL DEFECT - RETROSPECTIVE PENAL LAW (Art. 20(1) Constitution & Sec. 358 BNS / Sec. 531 BNSS)]: "
                    f"Date of alleged offence ({offence_date_str}) is PRIOR to 01-07-2024, but provisions of BNS, 2023 are invoked. "
                    f"Substantive offences prior to 01-07-2024 must be governed solely by the Indian Penal Code, 1860."
                )
            elif off_date >= cutoff_date and ("ipc" in text_lower or "indian penal code" in text_lower) and "bns" not in text_lower:
                defects.append(
                    f"[STATUTORY DEFECT - REPEALED CODE INVOKED]: Date of alleged offence ({offence_date_str}) is ON OR AFTER 01-07-2024, "
                    f"but FIR invokes repealed IPC provisions instead of the Bharatiya Nyaya Sanhita, 2023 (BNS)."
                )
        except ValueError:
            pass

    # 2. Check Section 35(3) BNSS / Section 41A CrPC Mandatory Notice Compliance
    if any(k in text_lower for k in ["420", "318", "406", "316", "498a", "85", "506", "351", "arrested"]):
        if "41a" not in text_lower and "35(3)" not in text_lower and "notice" not in text_lower:
            defects.append(
                "[MANDATORY ARREST SAFEGUARD VIOLATION - Sec. 35(3) BNSS / Sec. 41A CrPC]: "
                "No record of issuance/service of mandatory Notice of Appearance prior to arrest for offences punishable up to 7 years."
            )
            citations.append("Arnesh Kumar v. State of Bihar, (2014) 8 SCC 273 & Satender Kumar Antil v. CBI, (2022) 10 SCC 51")

    # 3. Check Written Grounds of Arrest (Art. 22(1) Constitution & Sec. 47/48 BNSS / Sec. 50/50A CrPC)
    if "arrest" in text_lower and "written grounds" not in text_lower:
        defects.append(
            "[CONSTITUTIONAL DEFECT - Art. 22(1) & Sec. 47/48 BNSS (Sec. 50/50A CrPC)]: "
            "Failure to furnish written grounds of arrest to the accused and nominated relative/friend forthwith in writing."
        )
        citations.append("Prabir Purkayastha v. State (NCT of Delhi), (2024) 8 SCC 254 & Pankaj Bansal v. Union of India, (2024) 7 SCC 576")

    # 4. Check Civil/Commercial Dispute Cloaked as Criminal Conspiracy / Cheating
    if any(k in text_lower for k in ["contract", "agreement", "payment", "invoice", "loan", "commercial", "breach"]):
        defects.append(
            "[SUBSTANTIVE INGREDIENT DEFECT - Sec. 318(4) BNS (420 IPC) & Sec. 316(2) BNS (406 IPC)]: "
            "Mere breach of contract or non-payment of commercial dues does not constitute cheating unless fraudulent or dishonest "
            "intention is shown right at the inception of the transaction. Moreover, criminal breach of trust (Sec. 316 BNS / 406 IPC) "
            "and cheating (Sec. 318 BNS / 420 IPC) cannot ordinarily coexist on the same set of facts."
        )
        citations.append("State of Haryana v. Bhajan Lal, 1992 Supp (1) SCC 335; Lalit Chaturvedi v. State of U.P. (2024 SC); Delhi Race Club (1940) Ltd. v. State of U.P. (2024 SC)")

    # 5. Check Electronic Evidence Certificate (Sec. 63(4) BSA / Sec. 65B(4) IEA)
    if any(k in text_lower for k in ["whatsapp", "email", "cctv", "audio", "video", "call recording", "digital", "screenshot"]):
        if "63(4)" not in text_lower and "65b" not in text_lower:
            defects.append(
                "[EVIDENTIARY DEFECT - Sec. 63(4) BSA, 2023 / Sec. 65B(4) IEA, 1872]: "
                "Reliance placed on electronic/digital records (WhatsApp/Email/CCTV/Audio) without accompanying mandatory "
                "certificate signed by the person in charge of the device and an expert under Section 63(4) of BSA, 2023."
            )
            citations.append("Arjun Panditrao Khotkar v. Kailash Kushanrao Gorantyal, (2020) 7 SCC 1")

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = (
        "# SWEETYAI FORENSIC FIR & CHARGE SHEET DEFECT AUDIT\n"
        f"**Audited Source:** {source_label}\n"
        f"**Reported Offence Date:** {offence_date_str or 'Not specified'}\n"
        f"**Audit Timestamp:** {now_str}\n\n"
        "---\n\n"
        "## I. DETECTED PROCEDURAL, CONSTITUTIONAL & STATUTORY DEFECTS\n"
    )
    if defects:
        for i, d in enumerate(defects, 1):
            report += f"{i}. {d}\n\n"
    else:
        report += "- No immediate facial defects triggered; proceed with granular witness statement (Sec. 180 BNSS / 161 CrPC) contradiction check.\n\n"

    report += "## II. BINDING SUPREME COURT AUTHORITIES FOR DEFENCE SUBMISSION\n"
    for c in citations:
        report += f"- *{c}*\n"

    out_path = os.path.join(AUDIT_DIR, "latest_fir_defect_audit.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)

    print("\n" + report)
    print("=========================================================================")
    print(f"[Success] Forensic FIR Audit Report saved to -> '{out_path}'")
    print("=========================================================================\n")


def calculate_remand_and_limitation(remand_date_str, max_punishment_years):
    remand_date = datetime.datetime.strptime(remand_date_str, "%Y-%m-%d").date()

    # 1. Default Bail under Section 187(3) BNSS (Section 167(2) CrPC)
    # 90 days if offence punishable with death, life imprisonment, or imprisonment >= 10 years (Rakesh Kumar Paul v. State of Assam)
    # 60 days for all other offences
    is_90_day_category = max_punishment_years >= 10
    statutory_days = 90 if is_90_day_category else 60
    police_custody_window_days = 60 if is_90_day_category else 40

    # Including day of first remand in computation
    chargesheet_deadline = remand_date + datetime.timedelta(days=statutory_days - 1)
    default_bail_accrual_date = remand_date + datetime.timedelta(days=statutory_days)
    pc_outer_limit_date = remand_date + datetime.timedelta(days=police_custody_window_days - 1)

    # 2. Limitation for Taking Cognizance under Section 514 BNSS (Section 468 CrPC)
    if max_punishment_years == 0:
        limitation_str = "6 Months from date of offence (Fine-only offence — Sec. 514(2)(a) BNSS / Sec. 468(2)(a) CrPC)"
    elif max_punishment_years <= 1:
        limitation_str = "1 Year from date of offence (Punishable up to 1 year — Sec. 514(2)(b) BNSS / Sec. 468(2)(b) CrPC)"
    elif max_punishment_years <= 3:
        limitation_str = "3 Years from date of offence (Punishable >1 year up to 3 years — Sec. 514(2)(c) BNSS / Sec. 468(2)(c) CrPC)"
    else:
        limitation_str = "No statutory bar of limitation under Sec. 514 BNSS (Offence punishable > 3 years), subject to Art. 21 speedy trial principles."

    print("\n=== SweetyAI Statutory Remand, Default Bail & Limitation Calculator ===")
    print(f"First Remand Date             : {remand_date_str}")
    print(f"Max Prescribed Punishment     : {max_punishment_years} Year(s)")
    print("-----------------------------------------------------------------------")
    print(f"[1] Statutory / Default Bail (Sec. 187(3) BNSS / Sec. 167(2) CrPC):")
    print(f"  - Applicable Statutory Tier : {statutory_days} Days ({'Offence punishable >= 10 yrs / Life / Death' if is_90_day_category else 'Offence punishable < 10 yrs — Rakesh Kumar Paul (2017) 15 SCC 67'})")
    print(f"  - Charge Sheet Filing Limit : {chargesheet_deadline.strftime('%Y-%m-%d')} (Day {statutory_days})")
    print(f"  - Default Bail Right Accrues: {default_bail_accrual_date.strftime('%Y-%m-%d')} (Day {statutory_days + 1} — Indefeasible Right under Art. 21)")
    print(f"\n[2] Police Custody Outer Window (Sec. 187(2) BNSS):")
    print(f"  - Max 15 Days PC Permissible: Within initial {police_custody_window_days} days (ends on {pc_outer_limit_date.strftime('%Y-%m-%d')})")
    print(f"\n[3] Cognizance Limitation Period (Sec. 514 BNSS / Sec. 468 CrPC):")
    print(f"  - Limitation Rule           : {limitation_str}")
    print("=======================================================================\n")
