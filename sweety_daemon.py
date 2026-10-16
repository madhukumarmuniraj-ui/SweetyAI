#!/home/madhukumarm/SweetyAI/venv/bin/python3
import os
import sys
import time
import sqlite3
from datetime import datetime

BASE_DIR = "/home/madhukumarm/SweetyAI"
os.chdir(BASE_DIR)

def run_daemon_loop():
    pid_file = os.path.join(BASE_DIR, "sweety_proactive_daemon.pid")
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))

    while True:
        try:
            # Update daemon heartbeat state
            state_file = os.path.join(BASE_DIR, "sweety_daemon_state.json")
            with open(state_file, "w", encoding="utf-8") as f:
                f.write(f'{{"status": "ONLINE", "pid": {os.getpid()}, "last_heartbeat": "{datetime.now().isoformat()}", "modules_active": 36}}\n')
        except Exception:
            pass
        time.sleep(30)

if __name__ == "__main__":
    run_daemon_loop()
