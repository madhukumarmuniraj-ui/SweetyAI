import sqlite3
import requests

NTFY_TOPIC = "sweetyai_secure_docket_9912"

def send_free_push_alert():
    try:
        conn = sqlite3.connect("sweety_cases.db")
        cur = conn.cursor()
        cur.execute("SELECT case_number, client_name, court, hearing_date, status FROM cases LIMIT 5;")
        cases = cur.fetchall()
        conn.close()

        if not cases:
            msg = "No active hearings logged for today."
        else:
            msg = "Cause List / Hearings:\n"
            for c_no, client, court, h_date, status in cases:
                msg += f"- {c_no} | {client} | {court} | {h_date} ({status})\n"

        # Explicitly encode payload as utf-8 bytes to prevent latin-1 errors
        response = requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=msg.encode('utf-8'),
            headers={
                "Title": "SweetyAI Court Briefing",
                "Priority": "high"
            }
        )
        if response.status_code == 200:
            print("[✓] Free push notification sent to your phone channel!")
        else:
            print(f"[!] Server returned status {response.status_code}")
    except Exception as e:
        print(f"[!] Notification error: {e}")

if __name__ == "__main__":
    send_free_push_alert()
