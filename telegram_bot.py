import os
import sys
import sqlite3
import urllib.request
import urllib.parse
import json
from datetime import date

DB_PATH = os.path.join("diary_data", "advocate_diary.db")
CONFIG_DB = os.path.join("social_config", "gateway_credentials.db")

def get_telegram_credentials():
    if not os.path.exists(CONFIG_DB):
        return None, None
    conn = sqlite3.connect(CONFIG_DB)
    c = conn.cursor()
    try:
        c.execute("SELECT api_key, api_secret FROM platforms WHERE platform_name='telegram'")
        row = c.fetchone()
        conn.close()
        if row:
            return row[0], row[1] # api_key is Bot Token, api_secret is Chat ID
    except Exception:
        conn.close()
    return None, None

def send_telegram_message(message_text):
    bot_token, chat_id = get_telegram_credentials()
    if not bot_token or not chat_id:
        print("[Error] Telegram credentials not found! Run connection command first:")
        print("  python3 sweety.py social connect --platform telegram --key 'BOT_TOKEN' --secret 'CHAT_ID'")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "Markdown"
    }
    
    data = urllib.parse.urlencode(payload).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            if res_data.get("ok"):
                print("[Success] SweetyAI Daily Briefing successfully pushed to Telegram!")
            else:
                print(f"[Error] Telegram API error: {res_data}")
    except Exception as e:
        print(f"[Error] Failed to connect to Telegram API: {e}")

def build_briefing_text():
    if not os.path.exists(DB_PATH):
        return "⚖️ *SweetyAI Daily Briefing*\nNo database found."
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    today_str = date.today().strftime("%Y-%m-%d")

    c.execute("SELECT hearing_time, court_hall, case_no, parties, stage FROM hearings WHERE hearing_date=?", (today_str,))
    hearings = c.fetchall()

    c.execute("SELECT priority, description FROM tasks WHERE status='PENDING' LIMIT 5")
    tasks = c.fetchall()
    conn.close()

    msg = f"⚖️ *SWEETYAI EXECUTIVE BRIEFING*\n*Date:* {date.today().strftime('%d-%m-%Y (%A)')}\n\n"
    
    msg += f"🏛️ *TODAY'S HEARINGS ({len(hearings)}):*\n"
    if not hearings:
        msg += "  • No hearings scheduled for today.\n"
    for h_time, court, caseno, parties, stage in hearings:
        msg += f"  • *{h_time}* | {caseno} ({parties})\n    _Forum: {court} | Stage: {stage}_\n"

    msg += f"\n📋 *TOP CHAMBER TASKS ({len(tasks)}):*\n"
    if not tasks:
        msg += "  • All tasks completed!\n"
    for prio, desc in tasks:
        msg += f"  • [{prio}] {desc}\n"

    msg += "\n_Sent securely from your air-gapped SweetyAI workstation._"
    return msg

if __name__ == "__main__":
    msg = build_briefing_text()
    send_telegram_message(msg)
