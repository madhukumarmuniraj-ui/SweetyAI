import os
import sys
import re
import hashlib
import datetime
import difflib
import argparse

SEC63_OUT_DIR = "sec63_certificates"
CUSTODY_OUT_DIR = "custody_bail_reports"
CROSSEXAM_OUT_DIR = "cross_examination_matrices"
DOWNLOADS_DIR = os.path.expanduser("~/Downloads")


def get_latest_download():
    if not os.path.exists(DOWNLOADS_DIR):
        return None
    files = [
        os.path.join(DOWNLOADS_DIR, f)
        for f in os.listdir(DOWNLOADS_DIR)
        if os.path.isfile(os.path.join(DOWNLOADS_DIR, f)) and not f.startswith(".")
    ]
    if not files:
        return None
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


# ==============================================================================
# MODULE 11: SECTION 63(4) BSA ELECTRONIC EVIDENCE CERTIFICATE & SHA-256 HASHER
# ==============================================================================
def generate_sec63_certificate(file_path, deponent_name="[Name of Deponent]", device_desc="Computer System / Mobile Device"):
    os.makedirs(SEC63_OUT_DIR, exist_ok=True)

    if os.path.isdir(file_path):
        candidates = [
            os.path.join(file_path, f)
            for f in os.listdir(file_path)
            if os.path.isfile(os.path.join(file_path, f)) and not f.startswith(".")
        ]
        if not candidates:
            print(f"[Error] No files found in '{file_path}'.")
            return
        candidates.sort(key=os.path.getmtime, reverse=True)
        file_path = candidates[0]

    if not os.path.exists(file_path):
        print(f"[Error] File '{file_path}' not found.")
        return

    sha256_hash = hashlib.sha256()
    sha512_hash = hashlib.sha512()
    md5_hash = hashlib.md5()

    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256_hash.update(chunk)
            sha512_hash.update(chunk)
            md5_hash.update(chunk)

    sha256_hex = sha256_hash.hexdigest().upper()
    sha512_hex = sha512_hash.hexdigest().upper()
    md5_hex = md5_hash.hexdigest().upper()

    stat = os.stat(file_path)
    file_size_bytes = stat.st_size
    file_size_kb = file_size_bytes / 1024.0
    mtime_str = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%d-%m-%Y %H:%M:%S")
    today_str = datetime.datetime.now().strftime("%d-%m-%Y")
    base_name = os.path.basename(file_path)
    ext = os.path.splitext(base_name)[1].upper().lstrip(".") or "BINARY/TEXT"

    cert_md = f"""# IN THE HIGH COURT OF KARNATAKA / COMPETENT TRIAL COURT AT BENGALURU

## CERTIFICATE UNDER SECTION 63(4) READ WITH THE SCHEDULE OF THE BHARATIYA SAKSHYA ADHINIYAM, 2023
*(Formerly Section 65B(4) of the Indian Evidence Act, 1872 — Per Arjun Panditrao Khotkar v. Kailash Kushanrao Gorantyal, (2020) 7 SCC 1)*

---

## PART A
*(To be filled by the Party / Person in Lawful Control of the Computer or Communication Device)*

I, **{deponent_name}**, aged about ____ years, residing at / operating from Bengaluru, Karnataka, do hereby solemnly affirm and state as follows:

1. **Description of Electronic Record Produced:**
   - **File Name:** `{base_name}`
   - **File Format / Type:** `{ext} Electronic Record`
   - **Exact File Size:** `{file_size_bytes:,} bytes ({file_size_kb:.2f} KB)`
   - **Last Modified Timestamp:** `{mtime_str}`

2. **Identification of Device & Lawful Control (Section 63(2) & (4) BSA, 2023):**
   - The aforesaid electronic output was produced from `{device_desc}` which has been in my regular, lawful control and exclusive custody during the relevant period.
   - Make / Model / Serial / MAC Details: `[Insert Make / Model / Serial No. of Laptop, Server, or Mobile Device]`

3. **Statutory Conditions under Section 63(2)(a)–(d) of the Bharatiya Sakshya Adhiniyam, 2023:**
   - **(a)** The electronic record was produced by the said computer/communication device during the period over which the computer was used regularly to create, store, or process information for the purposes of activities regularly carried on over that period;
   - **(b)** During the said period, information of the kind contained in the electronic record was regularly fed into the computer in the ordinary course of the said activities;
   - **(c)** Throughout the material part of the said period, the computer/device was operating properly, and there were no operational malfunctions affecting the accuracy or integrity of the electronic record or its contents; and
   - **(d)** The information contained in the electronic output reproduces or is derived from the information fed into the computer in the ordinary course of the said activities.

**Date:** {today_str}  
**Place:** Bengaluru  

**_______________________________**  
**SIGNATURE OF THE PARTY / DEPONENT**  
*({deponent_name})*

---

## PART B
*(To be filled by the Expert / Cryptographic Hash Verifier under The Schedule to the Bharatiya Sakshya Adhiniyam, 2023)*

I, **[Name & Designation of Examiner / Certifying Person]**, do hereby certify that the electronic record described in Part A (`{base_name}`, `{file_size_bytes:,} bytes`) has been cryptographically processed and verified, and its unbroken digital fingerprint / hash value is recorded below:

| Cryptographic Algorithm | Computed Hash Value / Digital Fingerprint |
| :--- | :--- |
| **SHA-256 Hash (Primary Statutory Standard)** | `{sha256_hex}` |
| **MD5 Checksum (Legacy Cross-Check)** | `{md5_hex}` |
| **SHA-512 Digest (Truncated 64-char Prefix)** | `{sha512_hex[:64]}...` |

I certify that the computer output / media bearing the above SHA-256 cryptographic hash is an exact, unaltered bit-for-bit reproduction of the source electronic record.

**Date:** {today_str}  
**Place:** Bengaluru  

**_______________________________**  
**SIGNATURE & SEAL OF EXAMINER / CERTIFIER**
"""

    slug = re.sub(r"[^A-Za-z0-9_\-]", "_", base_name)
    out_path = os.path.join(SEC63_OUT_DIR, f"sec63_bsa_certificate_{slug}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(cert_md)

    print("\n=== SweetyAI Section 63(4) BSA Electronic Evidence Hasher ===")
    print(f"Target File : {file_path} ({file_size_bytes:,} bytes)")
    print(f"SHA-256     : {sha256_hex}")
    print(f"MD5         : {md5_hex}")
    print("=========================================================================")
    print(f"[Success] Section 63(4) BSA Certificate (Part A & B) saved -> '{out_path}'")
    print(f"          (Run `python3 sweety.py export {out_path}` for A4 High Court HTML)")
    print("=========================================================================\n")


# ==============================================================================
# MODULE 12: SECTION 187 BNSS REMAND, POLICE CUSTODY & DEFAULT BAIL CALCULATOR
# ==============================================================================
def calculate_sec187_custody(remand_date_str, tier="60", chargesheet_filed=False):
    os.makedirs(CUSTODY_OUT_DIR, exist_ok=True)
    try:
        remand_date = datetime.datetime.strptime(remand_date_str, "%Y-%m-%d").date()
    except ValueError:
        print(f"[Error] Invalid date '{remand_date_str}'. Use YYYY-MM-DD.")
        return

    today = datetime.date.today()
    max_custody_days = 90 if str(tier) == "90" else 60
    pc_window_days = 60 if max_custody_days == 90 else 40

    # Per Enforcement Directorate v. Kapil Wadhawan, (2024) 7 SCC 147 (3-Judge Bench):
    # The date of first remand IS INCLUDED in computing the 60/90-day period.
    # Therefore, Day 1 = remand_date; Day 60 = remand_date + 59 days; Default Bail accrues on Day 61.
    pc_window_end = remand_date + datetime.timedelta(days=pc_window_days - 1)
    statutory_60_or_90_end = remand_date + datetime.timedelta(days=max_custody_days - 1)
    default_bail_accrual_date = remand_date + datetime.timedelta(days=max_custody_days)

    elapsed_days = (today - remand_date).days + 1  # Inclusive of remand day

    if chargesheet_filed:
        bail_status = "CHARGESHEET FILED under Sec. 193 BNSS (Right to Default Bail extinguished if filed prior to accrual; seek Regular Bail under Sec. 480 / 483 BNSS)."
    elif today >= default_bail_accrual_date:
        overdue = (today - default_bail_accrual_date).days + 1
        bail_status = f"INDEFEASIBLE RIGHT TO DEFAULT BAIL ACCRUED under Section 187(3) BNSS! (Accrued {overdue} day(s) ago on {default_bail_accrual_date.strftime('%d-%m-%Y')})"
    else:
        rem = (default_bail_accrual_date - today).days
        bail_status = f"IN STATUTORY CUSTODY PERIOD ({rem} day(s) remaining until Default Bail accrues on {default_bail_accrual_date.strftime('%d-%m-%Y')})"

    if today <= pc_window_end:
        pc_status = f"ACTIVE — Police Custody (up to 15 days total in tranches) remains permissible until {pc_window_end.strftime('%d-%m-%Y')} (Day {pc_window_days})."
    else:
        pc_status = f"EXPIRED — The {pc_window_days}-day outer window for Police Custody under Section 187(2) BNSS expired on {pc_window_end.strftime('%d-%m-%Y')}. Only Judicial Custody is permissible."

    offence_desc = (
        "Offence punishable with Death, Imprisonment for Life, or Imprisonment for a term of NOT LESS than 10 years (Section 187(3)(i) BNSS)"
        if max_custody_days == 90
        else "Offence punishable with Imprisonment up to 10 years / Other Offences (Section 187(3)(ii) BNSS; see Rakesh Kumar Paul v. State of Assam, (2017) 15 SCC 67)"
    )

    report = f"""# SWEETYAI SECTION 187 BNSS REMAND, POLICE CUSTODY & DEFAULT BAIL AUDIT
*(Under Section 187(2) & 187(3) of the Bharatiya Nagarik Suraksha Sanhita, 2023 — formerly Section 167(2) CrPC)*

| Remand & Custody Parameter | Statutory Computation |
| :--- | :--- |
| **Offence Classification** | {offence_desc} |
| **Date of First Judicial/Police Remand (Day 1)** | **{remand_date.strftime('%d-%m-%Y')}** *(Included per ED v. Kapil Wadhawan, (2024) 7 SCC 147)* |
| **Total Custody Elapsed (as of {today.strftime('%d-%m-%Y')})** | **{max(0, elapsed_days)} Day(s)** |
| **15-Day Police Custody Tranche Window** | First **{pc_window_days} Days** — Ends on **{pc_window_end.strftime('%d-%m-%Y')}** (Section 187(2) BNSS) |
| **Police Custody Eligibility Today** | `{pc_status}` |
| **Last Day of {max_custody_days}-Day Investigation Window** | **{statutory_60_or_90_end.strftime('%d-%m-%Y')}** (Day {max_custody_days}) |
| **Date Indefeasible Default Bail Accrues (Day {max_custody_days + 1})** | **{default_bail_accrual_date.strftime('%d-%m-%Y')}** |
| **DEFAULT BAIL STATUS (Section 187(3) BNSS)** | **`{bail_status}`** |

---

## II. CONTROLLING SUPREME COURT AUTHORITIES FOR BAIL / REMAND HEARING
1. **Inclusion of Remand Date:** *Enforcement Directorate v. Kapil Wadhawan*, (2024) 7 SCC 147 (3-Judge Bench) — The day on which the Magistrate first remands the accused is **included** in calculating the 60/90-day statutory period.
2. **60 vs. 90 Days ('Not Less Than 10 Years'):** *Rakesh Kumar Paul v. State of Assam*, (2017) 15 SCC 67 — Offences punishable "up to 10 years" (where 10 years is the maximum, not the mandatory minimum) attract the **60-day** period under Section 187(3)(ii) BNSS, not 90 days.
3. **Indefeasible Right Upon Filing Application:** *Uday Mohanlal Acharya v. State of Maharashtra*, (2001) 5 SCC 453 & *M. Ravindran v. Intelligence Officer, DRI*, (2021) 2 SCC 485 — Once the accused avails the right by filing an application after expiry of 60/90 days and offers to furnish bail, subsequent filing of a charge-sheet under Section 193 BNSS cannot defeat the right.
4. **Incomplete / Rushed Charge Sheet:** *Ritu Chhabaria v. Union of India*, 2023 SCC OnLine SC 502 — Filing an incomplete charge-sheet without completing investigation solely to defeat default bail violates Article 21.
"""

    out_path = os.path.join(CUSTODY_OUT_DIR, f"sec187_custody_audit_{remand_date_str}_{max_custody_days}d.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)

    print("\n" + report)
    print("=========================================================================")
    print(f"[Success] Section 187 BNSS Custody & Default Bail Audit saved -> '{out_path}'")
    print("=========================================================================\n")


# ==============================================================================
# MODULE 13: SECTION 180 BNSS / SECTION 148 BSA WITNESS CONTRADICTION MATRIX
# ==============================================================================
def generate_cross_exam_matrix(stmt1_path, stmt2_path, witness_name="PW-1"):
    os.makedirs(CROSSEXAM_OUT_DIR, exist_ok=True)
    if not os.path.exists(stmt1_path) or not os.path.exists(stmt2_path):
        print(f"[Error] Ensure both statement files exist: '{stmt1_path}', '{stmt2_path}'")
        return

    with open(stmt1_path, "r", encoding="utf-8", errors="replace") as f1:
        text1 = f1.read()
    with open(stmt2_path, "r", encoding="utf-8", errors="replace") as f2:
        text2 = f2.read()

    sents1 = [s.strip() for s in re.split(r"(?:\r?\n|(?<=[\.\;\!])\s+)", text1) if len(s.strip()) > 10]
    sents2 = [s.strip() for s in re.split(r"(?:\r?\n|(?<=[\.\;\!])\s+)", text2) if len(s.strip()) > 10]

    matcher = difflib.SequenceMatcher(None, sents1, sents2)
    contradictions = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "replace":
            prior = " ".join(sents1[i1:i2])
            subsequent = " ".join(sents2[j1:j2])
            contradictions.append(("DIRECT VARIATION / IMPROVEMENT", prior, subsequent))
        elif tag == "insert":
            subsequent = " ".join(sents2[j1:j2])
            contradictions.append(("MATERIAL OMISSION IN PRIOR STATEMENT (IMPROVEMENT IN COURT)", "[OMITTED IN SECTION 180 BNSS / FIR STATEMENT]", subsequent))
        elif tag == "delete":
            prior = " ".join(sents1[i1:i2])
            contradictions.append(("ABANDONED / SUPPRESSED STATEMENT", prior, "[OMITTED IN SUBSEQUENT DEPOSITION]"))

    today_str = datetime.date.today().strftime("%d-%m-%Y")
    report = f"""# SWEETYAI WITNESS CONTRADICTION & CROSS-EXAMINATION MATRIX
*(Under Section 180(3) Proviso of BNSS, 2023 read with Section 148 of the Bharatiya Sakshya Adhiniyam, 2023)*

**Target Witness:** `{witness_name}`  
**Prior Statement (FIR / Sec. 180 BNSS):** `{stmt1_path}`  
**Subsequent Statement (Deposition / Chief):** `{stmt2_path}`  
**Date Prepared:** {today_str}  
**Material Contradictions / Improvements Isolated:** `{len(contradictions)}`

---

## I. CONTRADICTION & IMPROVEMENT MATRIX (TAHSILDAR SINGH STANDARD)

| # | Nature of Discrepancy | Prior Statement (Sec. 180 BNSS / FIR) | Subsequent Statement (Chief / Charge Sheet) |
| :--- | :--- | :--- | :--- |
"""
    if contradictions:
        for idx, (kind, p_txt, s_txt) in enumerate(contradictions, 1):
            p_clean = p_txt.replace("|", "-")[:180]
            s_clean = s_txt.replace("|", "-")[:180]
            report += f"| {idx}. | **{kind}** | {p_clean} | {s_clean} |\n"
    else:
        report += "| 1. | `NO VARIATION` | Statements are identical. | Statements are identical. |\n"

    report += """
---

## II. MANDATORY TWO-STEP CONFRONTATION PROTOCOL (SECTION 148 BSA, 2023)
*(Per Tahsildar Singh v. State of U.P., AIR 1959 SC 1012 & V.K. Mishra v. State of Uttarakhand, (2015) 9 SCC 588)*

"""
    for idx, (kind, p_txt, s_txt) in enumerate(contradictions[:6], 1):
        report += f"### Contradiction #{idx}: {kind}\n"
        if "OMITTED IN SECTION 180" in p_txt:
            report += (
                f"- **Step 1 (To {witness_name} in Cross-Examination):** *\"I put it to you that in your initial statement recorded by the Police under Section 180 BNSS (Ex. D-__), you NEVER stated that '{s_txt[:120]}', and you are stating this for the first time before this Hon'ble Court as a tutored afterthought.\"*\n"
                f"- **Step 2 (To the Investigating Officer PW-__ during Cross-Examination):** *\"Did {witness_name} state before you during investigation under Section 180 BNSS that '{s_txt[:120]}'?\"* (When IO answers 'No', the material omission is formally proved as a contradiction under the Explanation to Section 180 BNSS).\n\n"
            )
        else:
            report += (
                f"- **Step 1 (Draw Attention of {witness_name} under Sec. 148 BSA):** *\"In your examination-in-chief today, you stated '{s_txt[:100]}'. However, in your previous statement recorded on [Date], you stated '{p_txt[:100]}'.\"*\n"
                f"- **Step 2 (Confront & Mark Portion as Ex. D-{idx}):** Confront the witness with the specific passage `{p_txt[:80]}` and have the trial court mark the contradicted portion as **Exhibit D-{idx}** for formal proof through the Investigating Officer.\n\n"
            )

    out_path = os.path.join(CROSSEXAM_OUT_DIR, f"cross_exam_matrix_{witness_name.lower().replace(' ', '_')}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)

    print("\n" + report)
    print("=========================================================================")
    print(f"[Success] Cross-Examination Contradiction Matrix saved -> '{out_path}'")
    print("=========================================================================\n")


def handle_suite_cli(cmd, argv):
    if cmd == "sec63-cert":
        parser = argparse.ArgumentParser(prog="sweety legal sec63-cert", description="Generate Section 63(4) BSA Electronic Evidence Certificate with SHA-256 hash.")
        parser.add_argument("file", nargs="?", help="Path to electronic file")
        parser.add_argument("--latest", action="store_true", help="Hash and certify the newest file in ~/Downloads")
        parser.add_argument("--deponent", default="[Name of Deponent / Custodian]", help="Name of person in charge of device")
        parser.add_argument("--device", default="Workstation / Mobile Device", help="Device description")
        args = parser.parse_args(argv)
        target = get_latest_download() if args.latest else args.file
        if not target:
            parser.print_help()
            return
        generate_sec63_certificate(target, args.deponent, args.device)

    elif cmd == "custody-calc":
        parser = argparse.ArgumentParser(prog="sweety legal custody-calc", description="Section 187 BNSS Remand, Police Custody (40/60d) & Default Bail (60/90d) Calculator.")
        parser.add_argument("--remand-date", required=True, help="Date of first judicial/police remand (YYYY-MM-DD)")
        parser.add_argument("--tier", choices=["60", "90"], default="60", help="60 days (up to 10 yrs) or 90 days (death/life/not less than 10 yrs)")
        parser.add_argument("--chargesheet-filed", action="store_true", help="Flag if Final Report under Sec. 193 BNSS is already filed")
        args = parser.parse_args(argv)
        calculate_sec187_custody(args.remand_date, args.tier, args.chargesheet_filed)

    elif cmd == "cross-exam":
        parser = argparse.ArgumentParser(prog="sweety legal cross-exam", description="Section 180 BNSS / Section 148 BSA Witness Contradiction & Cross-Examination Generator.")
        parser.add_argument("prior_statement", help="Path to FIR or Section 180 BNSS statement")
        parser.add_argument("subsequent_statement", help="Path to Chief Examination or Charge Sheet statement")
        parser.add_argument("--witness", default="PW-1", help="Witness identifier (e.g., PW-1)")
        args = parser.parse_args(argv)
        generate_cross_exam_matrix(args.prior_statement, args.subsequent_statement, args.witness)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        handle_suite_cli(sys.argv[1], sys.argv[2:])
    else:
        print("Usage: python3 trial_and_evidence_suite.py [sec63-cert | custody-calc | cross-exam] ...")
