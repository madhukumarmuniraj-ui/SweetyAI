import subprocess
import sys
import os

tests = [
    ("Module 2: Plugin Registry", ["python3", "sweety.py", "plugin"]),
    ("Module 3: Clause Redliner", ["python3", "sweety.py", "legal", "parallel", "breach of confidentiality"]),
    ("Module 4: Contract Reviewer", ["python3", "sweety.py", "legal", "review", "--help"]),
    ("Module 5: Privacy PII Auditor", ["python3", "sweety.py", "legal", "privacy-audit", "--help"]),
    ("Module 6: Citation Verifier", ["python3", "sweety.py", "legal", "verify-citations", "--help"]),
    ("Module 7: HC Chronology Extractor", ["python3", "sweety.py", "legal", "chronology", "--help"]),
    ("Module 8: Karnataka Court Fee Calc", ["python3", "sweety.py", "calc-fees", "--type", "commercial", "--value", "2500000", "--cause-date", "2026-01-01"]),
    ("Module 11: Sec. 63(4) BSA Certifier", ["python3", "sweety.py", "legal", "sec63-cert", "--help"]),
    ("Module 12: Sec. 187 Custody Calc", ["python3", "sweety.py", "legal", "custody-calc", "--remand-date", "2026-06-01", "--tier", "60"]),
    ("Module 13: Witness Contradiction", ["python3", "sweety.py", "legal", "cross-exam", "--help"]),
    ("Module 14: Bail Petition Suite", ["python3", "sweety.py", "legal", "bail", "--type", "482", "--forum", "hc", "--crime-no", "Crime 215/2026"]),
    ("Module 15: NI Act Sec. 138 PCR", ["python3", "sweety.py", "legal", "ni138", "--cheque-no", "884512", "--amount", "1500000", "--cheque-date", "2026-06-01", "--return-date", "2026-07-10", "--notice-date", "2026-07-20"]),
    ("Module 16: Full Master Case Packet", ["python3", "sweety.py", "legal", "full-audit", "--help"]),
    ("Module 17/18: DOCX/XLSX Boost", ["python3", "sweety.py", "legal", "claim-xlsx", "--principal", "2500000", "--rate", "18", "--start-date", "2025-01-15", "--regime", "sec34_cpc"]),
    ("Module 19: Karnataka Stamp Duty Calc", ["python3", "sweety.py", "legal", "stamp-duty", "--instrument", "conveyance_urban", "--value", "7500000"]),
    ("Module 20: Criminal Appeal Sec. 430", ["python3", "sweety.py", "legal", "crl-appeal", "--cc-no", "C.C. 18450/2024", "--judgment-date", "2026-09-25", "--fine", "1500000", "--sentence-months", "6", "--forum", "sessions"]),
    ("Module 21: NCLT / IBC Sec. 8 & 9", ["python3", "sweety.py", "legal", "ibc", "--principal", "11500000", "--rate", "18", "--default-date", "2025-11-10", "--invoice-no", "INV-BLR-2025-904"]),
    ("Module 22: Arbitration Sec. 21/9/11", ["python3", "sweety.py", "legal", "arbitration", "--contract-date", "2024-06-15", "--clause-no", "19.2", "--claim-amount", "4500000", "--default-date", "2025-12-01"]),
    ("Module 23: HC Quashing & Writ", ["python3", "sweety.py", "legal", "hc-quash", "--crime-no", "Crime 312/2026", "--fir-date", "2026-08-14", "--mode", "crlp528"]),
    ("Module 24: Commercial Suit & PIM", ["python3", "sweety.py", "legal", "comm-suit", "--principal", "3800000", "--rate", "18", "--cause-date", "2025-10-01"]),
    ("Module 25: Order XXI CPC Execution", ["python3", "sweety.py", "legal", "execution", "--case-no", "A.C. 88/2025", "--decree-date", "2026-03-10", "--amount", "4200000", "--arbitral-award"]),
    ("Module 26: MSME Sec. 18 & 3x RBI", ["python3", "sweety.py", "legal", "msme", "--acceptance-date", "2025-11-01", "--principal", "2800000"]),
    ("Module 27: Family Court Suite", ["python3", "sweety.py", "legal", "family-court", "--mode", "sec144", "--amount", "30000.0"])
]

passed = 0
failed = 0

print("=========================================================================")
print("          SWEETYAI 27-MODULE AUTOMATED INTEGRATION TEST SUITE            ")
print("=========================================================================\n")

for name, cmd in tests:
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=5)
        if res.returncode == 0:
            print(f"[PASS] {name}")
            passed += 1
        else:
            print(f"[FAIL] {name} (Exit code {res.returncode})")
            print(res.stdout[:300])
            failed += 1
    except Exception as e:
        print(f"[ERROR] {name}: {e}")
        failed += 1

print("\n=========================================================================")
print(f"TEST RESULTS: {passed} Passed, {failed} Failed out of {len(tests)} modules.")
print("=========================================================================\n")
