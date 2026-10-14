import os
import sys
import sqlite3
import urllib.parse
import webbrowser
import argparse
from datetime import date

DB_PATH = os.path.join("diary_data", "advocate_diary.db")

def format_phone(phone_str):
    digits = "".join(ch for ch in str(phone_str) if ch.isdigit())
    if len(digits) == 10:
        return "91" + digits
    if len(digits) == 12 and digits.startswith("91"):
        return digits
    return digits

def send_whatsapp_native(phone_number, case_no, court, h_date, h_time, stage):
    clean_ph = format_phone(phone_number)
    message = (
        f"⚖️ *COURT HEARING REMINDER* ⚖️\n"
        f"Chamber of Madhukumar Muniraj, Advocate\n\n"
        f"• *Case No:* {case_no}\n"
        f"• *Forum:* {court}\n"
        f"• *Date & Time:* {h_date} at {h_time}\n"
        f"• *Stage:* {stage}\n\n"
        f"Kindly be present at the Court Hall 15 minutes prior."
    )
    encoded = urllib.parse.quote(message)
    url = f"https://wa.me/{clean_ph}?text={encoded}" if clean_ph else f"https://wa.me/?text={encoded}"
    
    print(f"[Native WhatsApp Bot] Opening browser to message client ({phone_number}) for {case_no}...")
    webbrowser.open(url)
    print(f"[Success] WhatsApp Web/App protocol launched for {case_no}!")

def broadcast_today():
    if not os.path.exists(DB_PATH):
        print("[Error] Case Diary DB not found. Run `python3 sweety.py diary briefing` first.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    today_str = date.today().strftime("%Y-%m-%d")
    c.execute("SELECT case_no, court_hall, hearing_time, stage, client_phone FROM hearings WHERE hearing_date=?", (today_str,))
    rows = c.fetchall()
    conn.close()

    if not rows:
        print("[Native WhatsApp Bot] No hearings scheduled for today to broadcast.")
        return

    print(f"[Native WhatsApp Bot] Found {len(rows)} hearings today. Opening WhatsApp links...")
    for caseno, court, h_time, stage, phone in rows:
        if phone and phone != "N/A":
            send_whatsapp_native(phone, caseno, court, today_str, h_time, stage)
        else:
            print(f"[Skip] No valid client phone number logged for {caseno}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="native_wa_bot")
    parser.add_argument("--phone", help="Client phone number (e.g. 9845000001)")
    parser.add_argument("--caseno", default="Com.O.S. 125/2026")
    parser.add_argument("--court", default="CCH-83 Bengaluru")
    parser.add_argument("--date", default=date.today().strftime("%Y-%m-%d"))
    parser.add_argument("--time", default="10:30 AM")
    parser.add_argument("--stage", default="Hearing")
    parser.add_argument("--broadcast", action="store_true", help="Broadcast today's hearings")

    args = parser.parse_args()
    if args.broadcast:
        broadcast_today()
    elif args.phone:
        send_whatsapp_native(args.phone, args.caseno, args.court, args.date, args.time, args.stage)
    else:
        broadcast_today()
