import os
import subprocess

DAEMON_CODE = '''import time
import subprocess
from datetime import datetime

print("=========================================================================")
print("     SWEETYAI LOCAL BACKGROUND SCHEDULER & MORNING BRIEFING DAEMON         ")
print("=========================================================================")
print(" -> Running 24/7 in local memory (Air-Gapped | Zero Telemetry)")
print(" -> Scheduled Trigger: Every day at 08:30 AM\\n")

while True:
    now = datetime.now()
    if now.hour == 8 and now.minute == 30:
        dt_str = now.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{dt_str}] Triggering Scheduled Morning Briefing...")
        try:
            subprocess.run(["python3", "sweety.py", "diary", "briefing", "--notify"], check=False)
        except Exception as e:
            print(f"[Error] Failed to run briefing: {e}")
        time.sleep(60)
    else:
        time.sleep(30)
'''

with open("sweety_daemon.py", "w", encoding="utf-8") as f:
    f.write(DAEMON_CODE)

with open("sweety_daemon.py", "rb") as f:
    compile(f.read(), "sweety_daemon.py", "exec")
print("[Compile Check] sweety_daemon.py compiled cleanly with 0 errors!")
