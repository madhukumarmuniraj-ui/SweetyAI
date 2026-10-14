import os
import sys
import sqlite3
import subprocess
from datetime import date

DB_PATH = os.path.join("diary_data", "advocate_diary.db")

def copy_to_clipboard(text):
    try:
        # Works on Linux X11/Wayland via xclip or wl-copy
        p = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
        p.communicate(input=text.encode('utf-8'))
        print("[Clipboard] Message successfully copied to your system clipboard!")
    except Exception:
        try:
            p = subprocess.Popen(['wl-copy'], stdin=subprocess.PIPE)
            p.communicate(input=text.encode('utf-8'))
            print("[Clipboard] Message successfully copied via wl-copy!")
        except Exception:
            print("[Error] Install 'xclip' or 'wl-clipboard' to enable automated clipboard copying.")

def get_latest_hearing_msg():
    if not os.path.exists(DB_PATH):
        return "No database found."
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    today_str = date.today().strftime("%Y-%m-%d")
    c.execute("SELECT hearing_time, court_hall, case_no, parties, stage FROM hearings WHERE hearing_date=? LIMIT 1", (today_str,))
    row = c.fetchone()
    conn.close()
    if not row:
        return "No hearings found for today."
    h_time, court, caseno, parties, stage = row
    return (
        f"⚖️ *COURT HEARING REMINDER* ⚖️\n"
        f"Chamber of Madhukumar Muniraj, Advocate\n\n"
        f"• *Case No:* {caseno} ({parties})\n"
        f"• *Forum:* {court}\n"
        f"• *Time & Stage:* {h_time} | {stage}\n\n"
        f"Kindly be present at the Court Hall 15 minutes prior."
    )

if __name__ == "__main__":
    msg = get_latest_hearing_msg()
    print("-------------------------------------------------------------------------")
    print(msg)
    print("-------------------------------------------------------------------------")
    copy_to_clipboard(msg)
    print("-> Just open your WhatsApp Desktop App and press Ctrl+V to send!")
