import subprocess

batch_jobs = [
    ("Karnataka Court Fee", ["python3", "sweety.py", "calc-fees", "--type", "commercial", "--value", "5000000", "--cause-date", "2026-01-01"]),
    ("Stamp Duty Report", ["python3", "sweety.py", "legal", "stamp-duty", "--instrument", "conveyance_urban", "--value", "5000000"]),
    ("Bail Petition", ["python3", "sweety.py", "legal", "bail", "--type", "regular", "--forum", "sessions", "--crime-no", "Crime 101/2026"]),
    ("NI Act Sec. 138 PCR", ["python3", "sweety.py", "legal", "ni138", "--cheque-no", "123456", "--amount", "1000000", "--cheque-date", "2026-09-01", "--presentation-date", "2026-09-05", "--dishonour-date", "2026-09-10", "--notice-date", "2026-09-15", "--service-date", "2026-09-20"]),
    ("Excel Claim Schedule (.XLSX)", ["python3", "sweety.py", "legal", "claim-xlsx", "--principal", "1000000", "--rate", "12", "--start-date", "2025-01-01", "--regime", "sec34_cpc"]),
    ("Criminal Appeal & Suspension", ["python3", "sweety.py", "legal", "crl-appeal", "--cc-no", "C.C. 500/2025", "--judgment-date", "2026-08-01", "--fine", "200000", "--sentence-months", "3", "--forum", "sessions"]),
    ("NCLT / IBC Demand Notice", ["python3", "sweety.py", "legal", "ibc", "--principal", "10000000", "--rate", "12", "--default-date", "2025-06-01", "--invoice-no", "INV-001"]),
    ("Arbitration Notice (Sec. 21)", ["python3", "sweety.py", "legal", "arbitration", "--contract-date", "2024-01-01", "--clause-no", "12.1", "--claim-amount", "2500000", "--default-date", "2025-05-01"]),
    ("HC Quashing Petition", ["python3", "sweety.py", "legal", "hc-quash", "--crime-no", "Crime 55/2026", "--fir-date", "2026-07-01", "--mode", "crlp528"]),
    ("Commercial Suit & PIM", ["python3", "sweety.py", "legal", "comm-suit", "--principal", "2000000", "--rate", "12", "--cause-date", "2025-08-01"]),
    ("Execution Petition (Order XXI)", ["python3", "sweety.py", "legal", "execution", "--case-no", "Com. Suit 10/2025", "--decree-date", "2026-02-01", "--amount", "2200000", "--commercial"]),
    ("MSMED Act Reference", ["python3", "sweety.py", "legal", "msme", "--acceptance-date", "2025-06-01", "--principal", "1500000"]),
    ("Family Court Maintenance (Sec. 144)", ["python3", "sweety.py", "legal", "family-court", "--mode", "sec144", "--amount", "25000"])
]

print("=========================================================================")
print("          GENERATING COMPLETE LEGAL SUITE SAMPLES IN ONE SHOT            ")
print("=========================================================================\n")

success_count = 0
for name, cmd in batch_jobs:
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if res.returncode == 0:
        print(f"[GENERATED] {name}")
        success_count += 1
    else:
        print(f"[FAILED]    {name}")

print(f"\n=========================================================================")
print(f"BATCH COMPLETE: {success_count} / {len(batch_jobs)} Legal Suites Executed Successfully.")
print("Files are now available in your local ~/SweetyAI subfolders.")
print("=========================================================================\n")
