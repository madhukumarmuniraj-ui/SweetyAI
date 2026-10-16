"""
SweetyAI Legal Workstation - Automated Cause List & Case Monitor
Scans for new docket updates, parses them, and triggers desktop notifications.
"""

import os
import sqlite3
import subprocess

DB_NAME = "sweety_cases.db"

def init_db_if_missing():
    """Ensures the database table exists."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number TEXT NOT NULL,
            client_name TEXT NOT NULL,
            court TEXT NOT NULL,
            hearing_date TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def send_desktop_notification(title, message):
    """Triggers a native Linux desktop notification via notify-send."""
    try:
        subprocess.run(["notify-send", title, message], check=True)
        print(f"[SweetyAI Monitor] Notification sent: {title}")
    except Exception as e:
        print(f"[SweetyAI Monitor] Could not send desktop notification: {e}")

def check_upcoming_hearings():
    """Checks the local database for pending cases and alerts you."""
    init_db_if_missing()
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT case_number, client_name, court, hearing_date FROM cases WHERE status = 'Pending'")
    pending_cases = cursor.fetchall()
    conn.close()

    if pending_cases:
        print(f"[SweetyAI Monitor] Found {len(pending_cases)} pending active cases in docket.")
        for case in pending_cases:
            case_num, client, court, h_date = case
            print(f" -> Case: {case_num} | Client: {client} | Court: {court} | Date: {h_date}")
        send_desktop_notification("SweetyAI Legal Docket", f"You have {len(pending_cases)} pending cases to review!")
    else:
        print("[SweetyAI Monitor] Database is active. No pending cases found.")

if __name__ == "__main__":
    print("Running SweetyAI Legal Monitor...")
    check_upcoming_hearings()
