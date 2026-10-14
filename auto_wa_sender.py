import urllib.request
import urllib.parse
import os
import sqlite3
from datetime import date

PHONE = "9845000001" # Replace with your 10-digit mobile number
APIKEY = "YOUR_CALLMEBOT_API_KEY" # Replace with your key

def send_whatsapp_api(message):
    encoded_msg = urllib.parse.quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE}&text={encoded_msg}&apikey={APIKEY}"
    try:
        req = urllib.request.urlopen(url)
        if req.status == 200:
            print("[Success] Automated WhatsApp message sent successfully via API!")
        else:
            print(f"[Error] Failed to send. Status code: {req.status}")
    except Exception as e:
        print(f"[Error] Connection failed: {e}")

if __name__ == "__main__":
    db_path = os.path.join("diary_data", "advocate_diary.db")
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        today = date.today().strftime("%Y-%m-%d")
        c.execute("SELECT case_no, court_hall, hearing_time FROM hearings WHERE hearing_date=?", (today,))
        rows = c.fetchall()
        conn.close()

        text = f"⚖️ *SweetyAI Daily Briefing*\n"
        for r in rows:
            text += f"• {r[0]} at {r[1]} ({r[2]})\n"
        send_whatsapp_api(text)
    else:
        send_whatsapp_api("⚖️ SweetyAI Daily Briefing: No hearings today.")
