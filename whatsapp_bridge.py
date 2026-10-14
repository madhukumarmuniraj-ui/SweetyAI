import os
import sys
import sqlite3
import urllib.parse
from datetime import date, datetime

DB_PATH = os.path.join("diary_data", "advocate_diary.db")

def generate_whatsapp_briefing_text():
    if not os.path.exists(DB_PATH):
        return "SweetyAI Diary DB not initialized yet. Run `python3 sweety.py diary briefing` first."
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    today_str = date.today().strftime("%Y-%m-%d")

    c.execute("SELECT hearing_time, court_hall, case_no, parties, stage FROM hearings WHERE hearing_date=?", (today_str,))
    today_hearings = c.fetchall()

    c.execute("SELECT priority, description FROM tasks WHERE status='PENDING' ORDER BY CASE priority WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 ELSE 3 END LIMIT 5")
    pending_tasks = c.fetchall()

    c.execute("SELECT case_no, event_type, outer_limit_date FROM deadlines ORDER BY outer_limit_date ASC LIMIT 3")
    deadlines = c.fetchall()
    conn.close()

    msg = f"*⚖️ SWEETYAI DAILY EXECUTIVE BRIEFING*\n*Date:* {date.today().strftime('%d-%m-%Y (%A)')}\n\n"
    
    msg += f"*🏛️ TODAY'S COURT HEARINGS ({len(today_hearings)}):*\n"
    if not today_hearings:
        msg += "  • No hearings scheduled for today.\n"
    for h_time, court, caseno, parties, stage in today_hearings:
        msg += f"  • *{h_time}* | {caseno} ({parties}) at {court}\n    _Stage: {stage}_\n"

    msg += f"\n*📋 TOP CHAMBER TASKS ({len(pending_tasks)}):*\n"
    if not pending_tasks:
        msg += "  • All tasks completed!\n"
    for prio, desc in pending_tasks:
        msg += f"  • [{prio}] {desc}\n"

    msg += f"\n*⏳ STATUTORY LIMITATION WATCHLIST:* \n"
    for caseno, ev, out_date in deadlines:
        msg += f"  • {caseno} - {ev} (Due: {out_date})\n"

    msg += "\n_Sent securely from your Air-Gapped SweetyAI Legal Workstation._"
    return msg

def get_whatsapp_url(phone_number=""):
    text = generate_whatsapp_briefing_text()
    encoded = urllib.parse.quote(text)
    clean_ph = "".join(ch for ch in str(phone_number) if ch.isdigit())
    if len(clean_ph) == 10:
        clean_ph = "91" + clean_ph
    
    if clean_ph:
        return f"https://wa.me/{clean_ph}?text={encoded}"
    else:
        return f"https://wa.me/?text={encoded}"

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "print":
        print(generate_whatsapp_briefing_text())
    else:
        url = get_whatsapp_url()
        print("=========================================================================")
        print("          SWEETYAI WHATSAPP DAILY BRIEFING URL GENERATED                 ")
        print("=========================================================================")
        print(url[:120] + "...\n")
        print("To open your daily WhatsApp briefing instantly, run:")
        print("  python3 -c 'import webbrowser; from whatsapp_bridge import get_whatsapp_url; webbrowser.open(get_whatsapp_url())'")
        print("=========================================================================")
