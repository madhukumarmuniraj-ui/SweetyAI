import os
import datetime

TRIAL_DIR = "trial_practice_outputs"


def generate_cross_examination(witness_type, case_facts):
    os.makedirs(TRIAL_DIR, exist_ok=True)
    today = datetime.datetime.now().strftime("%d-%m-%Y")

    if witness_type == "io":
        role_title = "INVESTIGATING OFFICER (PW — I.O.)"
        questions = [
            "1. **[Jurisdiction & FIR Registration — Sec. 173 BNSS / Sec. 154 CrPC]:** Witness is shown the original FIR. Is it true that there is an unexplained delay between the alleged time of occurrence and the dispatch of the FIR to the Jurisdictional Magistrate under Section 176 BNSS (Section 157 CrPC)?",
            "2. **[Mandatory Pre-Arrest Notice — Sec. 35(3) BNSS / Sec. 41A CrPC]:** Since the offence alleged carries a maximum punishment up to 7 years, did you record specific written reasons in the Case Diary under Section 35(1)(b) BNSS before affecting arrest, or serve a mandatory Notice of Appearance under Section 35(3) BNSS as mandated in *Arnesh Kumar v. State of Bihar, (2014) 8 SCC 273*?",
            "3. **[Written Grounds of Arrest — Sec. 47/48 BNSS & Art. 22(1) Constitution]:** Can you point out from the Arrest Memo or Case Diary any contemporaneous acknowledgement proving that written grounds of arrest were furnished forthwith to the accused in compliance with *Prabir Purkayastha v. State (NCT of Delhi), (2024) 8 SCC 254*?",
            "4. **[Electronic Evidence Seizure & Hash Value — Sec. 63(4) BSA / Sec. 65B(4) IEA]:** Did you generate and record the cryptographic hash value (SHA-256/MD5) at the time of seizing the electronic device/records, and is there a valid Part-A and Part-B certificate under Section 63(4) of the Bharatiya Sakshya Adhiniyam, 2023 on record?",
            "5. **[Proof of Omissions Under Sec. 148 BSA / Sec. 145 IEA read with Sec. 180 BNSS / Sec. 161 CrPC]:** Witness's attention is drawn to the Section 180 BNSS (161 CrPC) statement of PW-1. Is it true that PW-1 never stated before you during investigation the material facts now deposed for the first time before the Court (*Tahsildar Singh v. State of U.P., AIR 1959 SC 1012*)?",
        ]
    elif witness_type == "panch":
        role_title = "MAHAZAR / RECOVERY PANCH WITNESS (PW — PANCH)"
        questions = [
            "1. **[Sec. 105 BNSS Mandatory Audio-Video Recording of Search & Seizure]:** Was the alleged search and seizure videographed on a mobile phone or electronic device and forwarded without delay to the Magistrate as mandatorily required under **Section 105 of the Bharatiya Nagarik Suraksha Sanhita, 2023**?",
            "2. **[Independent Witness Credibility — Sec. 103(4) BNSS / Sec. 100(4) CrPC]:** Are you a local resident of the neighbourhood where the mahazar was drawn, or have you acted as a stock panch witness for the same Police Station in prior cases?",
            "3. **[Disclosure Statement Scope — Proviso to Sec. 23(2) BSA / Sec. 27 IEA]:** Were you personally present when the accused allegedly made the voluntary disclosure statement, and was the alleged spot of recovery already an open, publicly accessible place known to the police prior to the mahazar (*Pulukuri Kottaya v. King-Emperor, AIR 1947 PC 67*)?",
            "4. **[Sealing & Chain of Custody]:** Was the sample seal impression affixed on the mahazar on the spot and handed over to an independent witness, or was the mahazar prepared at the Police Station where you merely signed on the dotted line?",
        ]
    else:  # complainant
        role_title = "DEFACTO COMPLAINANT / INFORMANT (PW-1)"
        questions = [
            "1. **[Contradictions & Material Improvements — Sec. 148 BSA / Sec. 145 IEA]:** Attention of the witness is drawn to the written complaint (Ex. P-1) and Section 180 BNSS (161 CrPC) statement. You had not stated this specific overt act in your initial complaint; I put it to you that this is a subsequent improvement tutored for the purpose of this trial.",
            "2. **[Motive & Prior Civil/Commercial Dispute]:** Is it true that prior to lodging the present criminal complaint, there were pending civil/commercial account transactions between you and the accused, and no civil suit for recovery was instituted?",
            "3. **[Absence of Mens Rea at Inception — Sec. 318 BNS / Sec. 420 IPC]:** Is it true that the parties had regular course of dealings earlier, demonstrating that there was no fraudulent or dishonest inducement at the inception of the transaction?",
            "4. **[Delay in Lodging First Information — Sec. 173 BNSS / Sec. 154 CrPC]:** Despite having access to electronic communication (e-FIR under Sec. 173(1) BNSS) and the local police station, you waited several days/months before lodging the complaint after deliberation.",
        ]

    doc = (
        f"# SWEETYAI TRIAL CROSS-EXAMINATION STRATEGY (SEC. 143 & 148 BSA, 2023 / SEC. 138 & 145 IEA)\n"
        f"**Target Witness:** {role_title}\n"
        f"**Case Matrix:** {case_facts}\n"
        f"**Date Prepared:** {today}\n\n"
        f"---\n\n"
        f"## I. STATUTORY FOUNDATION FOR CONTRADICTION & IMPEACHMENT\n"
        f"- **Section 148 of Bharatiya Sakshya Adhiniyam, 2023 (Section 145 IEA):** Cross-examination as to previous statements in writing (must draw witness's attention to the specific parts before proving contradiction).\n"
        f"- **Section 181 Proviso BNSS, 2023 (Section 162 Proviso CrPC):** Using previous police statements recorded under Section 180 BNSS (Section 161 CrPC) to contradict prosecution witnesses in the manner provided by Section 148 BSA.\n"
        f"- **Section 105 BNSS, 2023:** Mandatory audio-video electronic recording of all search and seizure operations.\n"
        f"- **Binding Authority:** *Tahsildar Singh v. State of U.P., AIR 1959 SC 1012* (Omissions that amount to vital contradictions must be put to the witness and then proved through the Investigating Officer).\n\n"
        f"## II. STRUCTURED CROSS-EXAMINATION QUESTIONS\n"
        + "\n\n".join(questions)
        + "\n"
    )

    out_path = os.path.join(TRIAL_DIR, f"cross_exam_{witness_type}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(doc)

    print("\n" + doc)
    print("=========================================================================")
    print(f"[Success] Cross-Examination Matrix saved to -> '{out_path}'")
    print("=========================================================================\n")


def generate_section_63_bsa_certificate(device_desc, record_desc):
    os.makedirs(TRIAL_DIR, exist_ok=True)
    today = datetime.datetime.now().strftime("%d-%m-%Y")

    cert = (
        "# IN THE COURT OF THE HON'BLE MAGISTRATE / SESSIONS JUDGE AT BENGALURU\n"
        "**STATUTORY CERTIFICATE UNDER SECTION 63(4) OF THE BHARATIYA SAKSHYA ADHINIYAM, 2023**\n"
        "*(Read with The Schedule to BSA, 2023 — Formerly Section 65B(4) of the Indian Evidence Act, 1872)*\n\n"
        "---\n\n"
        "## PART A — TO BE FILLED BY THE PARTY / PERSON IN CHARGE OF THE COMPUTER OR COMMUNICATION DEVICE\n"
        "I, **[Name of Deponent]**, Aged about **[__]** years, S/o **[Father's Name]**, residing at **[Address, Bengaluru]**, do hereby solemnly affirm and certify as follows:\n\n"
        f"1. **Identification of Electronic Record:** I am producing the electronic record described as: **{record_desc}**.\n"
        f"2. **Device Particulars:** The said electronic record was produced by / stored in the computer/communication device: **{device_desc}** (Make/Model/Serial/IMEI/MAC Address).\n"
        "3. **Lawful Control & Regular Use (Sec. 63(2)(a) BSA):** During the relevant period, the said computer/communication device was kept in the regular course of activities and was under my lawful control and management.\n"
        "4. **Regular Input of Information (Sec. 63(2)(b) BSA):** Information of the kind contained in the electronic record was regularly fed into the said device in the ordinary course of the said activities.\n"
        "5. **Proper Operating Condition (Sec. 63(2)(c) BSA):** Throughout the material part of the said period, the computer/communication device was operating properly, and there were no operational malfunctions affecting the accuracy or integrity of the electronic record or its contents.\n"
        "6. **Cryptographic Hash Value (Schedule to BSA, 2023):**\n"
        "   - **SHA-256 Hash Value of File:** `[Insert 64-character SHA-256 Digest via 'sha256sum <file>']`\n\n"
        f"**Date:** {today} | **Place:** Bengaluru\n"
        "**Signature of the Party / Custodian**\n\n"
        "---\n\n"
        "## PART B — TO BE FILLED BY THE EXPERT (UNDER THE SCHEDULE TO SECTION 63(4)(c) BSA, 2023)\n"
        "I, **[Name of Certifying Expert / System Administrator]**, Designation: **[Designation/Qualification]**, do hereby certify that:\n"
        f"1. I have examined the electronic record (**{record_desc}**) extracted from **{device_desc}**.\n"
        "2. The computer output faithfully reproduces the information contained in the original electronic device, and the cryptographic SHA-256 hash value specified above has been verified and remains intact without tampering.\n\n"
        f"**Date:** {today} | **Place:** Bengaluru\n"
        "**Signature & Seal of the Expert**\n"
    )

    out_path = os.path.join(TRIAL_DIR, "certificate_sec_63_bsa_2023.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(cert)

    print("\n" + cert)
    print("=========================================================================")
    print(f"[Success] Section 63(4) BSA Certificate saved to -> '{out_path}'")
    print("=========================================================================\n")


def calculate_ni_act_138(dishonour_date_str, notice_served_date_str=None, cheque_amount="5,00,000"):
    os.makedirs(TRIAL_DIR, exist_ok=True)
    dishonour_date = datetime.datetime.strptime(dishonour_date_str, "%Y-%m-%d").date()

    # Proviso (b) to Sec. 138 NI Act: Legal Demand Notice must be dispatched within 30 days of receipt of bank return memo
    notice_dispatch_deadline = dishonour_date + datetime.timedelta(days=30)

    if notice_served_date_str:
        served_date = datetime.datetime.strptime(notice_served_date_str, "%Y-%m-%d").date()
    else:
        served_date = dishonour_date + datetime.timedelta(days=10)

    # Proviso (c) to Sec. 138 NI Act: Drawer has 15 days from receipt of notice to make payment (Saketh India Ltd. v. India Securities Ltd., (1999) 3 SCC 1)
    grace_period_end = served_date + datetime.timedelta(days=15)
    cause_of_action_date = grace_period_end + datetime.timedelta(days=1)

    # Sec. 142(1)(b) NI Act: Complaint must be filed within 1 month of the date on which cause of action arises
    complaint_deadline = cause_of_action_date + datetime.timedelta(days=30)

    summary = (
        "# SWEETYAI SECTION 138 NI ACT STATUTORY TIMELINE & DEMAND NOTICE AUDITOR\n"
        f"**Date of Bank Return Memo (Dishonour):** {dishonour_date_str}\n"
        f"**Cheque Amount:** INR {cheque_amount}\n\n"
        "---\n\n"
        "## I. MANDATORY STATUTORY TIMELINES (SECTIONS 138 & 142 NI ACT, 1881)\n"
        f"1. **30-Day Statutory Demand Notice Deadline [Sec. 138 Proviso (b)]:** Must be dispatched on or before **{notice_dispatch_deadline.strftime('%Y-%m-%d')}**.\n"
        f"2. **Date of Service of Notice on Drawer:** **{served_date.strftime('%Y-%m-%d')}** {'(User Provided)' if notice_served_date_str else '(Estimated +10 days)'}.\n"
        f"3. **15-Day Payment Grace Period Ends [Sec. 138 Proviso (c)]:** **{grace_period_end.strftime('%Y-%m-%d')}** *(Premature complaint filed before expiry of 15 clear days is not maintainable — Yogendra Pratap Singh v. Savitri Pandey, (2014) 10 SCC 713)*.\n"
        f"4. **Date Cause of Action Arises [Sec. 142(1)(b)]:** **{cause_of_action_date.strftime('%Y-%m-%d')}** *(Excluding day of service as per Saketh India Ltd. v. India Securities Ltd., (1999) 3 SCC 1)*.\n"
        f"5. **1-Month Limitation to File Complaint [Sec. 142(1)(b) NI Act & Sec. 223 BNSS / Sec. 200 CrPC]:** On or before **{complaint_deadline.strftime('%Y-%m-%d')}**.\n"
        "6. **Territorial Jurisdiction [Sec. 142(2)(a) NI Act]:** Court within whose local jurisdiction the branch of the bank where the **Payee / Holder in due course maintains the account** is situated (if presented for collection through an account).\n"
        "7. **Interim Compensation [Sec. 143A NI Act]:** Up to 20% of the cheque amount may be prayed for upon framing of plea (*Rakesh Ranjan Shrivastava v. State of Jharkhand, (2024) 4 SCC 419*).\n"
    )

    out_path = os.path.join(TRIAL_DIR, "ni_act_138_computation_and_notice.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(summary)

    print("\n" + summary)
    print("=========================================================================")
    print(f"[Success] NI Act 138 Statutory Audit saved to -> '{out_path}'")
    print("=========================================================================\n")
