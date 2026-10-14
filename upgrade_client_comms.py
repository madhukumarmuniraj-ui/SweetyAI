import os
import sys
import subprocess

def write_clean(filename, content):
    cleaned = content.replace("\u00a0", " ").replace("\u200b", "")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(cleaned)

# ==============================================================================
# 1. UPGRADE ADVOCATE_DIARY.PY WITH WHATSAPP & SMS CLIENT GENERATOR
# ==============================================================================
ADVOCATE_DIARY_CODE = r'''import os
import sys
import sqlite3
import urllib.parse
import argparse
import subprocess
from datetime import datetime, date, timedelta

DB_DIR = "diary_data"
DB_PATH = os.path.join(DB_DIR, "advocate_diary.db")
ICS_PATH = os.path.join(DB_DIR, "advocate_calendar.ics")
CLIENT_MSG_PATH = os.path.join(DB_DIR, "client_communications.md")
HTML_DASHBOARD = os.path.join("court_ready_exports", "daily_executive_dashboard.html")

def get_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS hearings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hearing_date TEXT,
        hearing_time TEXT,
        court_hall TEXT,
        case_no TEXT,
        cnr_no TEXT,
        parties TEXT,
        stage TEXT,
        client_phone TEXT,
        notes TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        due_date TEXT,
        priority TEXT,
        category TEXT,
        description TEXT,
        status TEXT DEFAULT 'PENDING'
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS deadlines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_no TEXT,
        event_type TEXT,
        trigger_date TEXT,
        statutory_date TEXT,
        outer_limit_date TEXT,
        statute_ref TEXT
    )""")
    conn.commit()
    return conn

def format_indian_phone(phone_str):
    digits = "".join(ch for ch in str(phone_str) if ch.isdigit())
    if len(digits) == 10:
        return "91" + digits
    if len(digits) == 12 and digits.startswith("91"):
        return digits
    return digits

def build_hearing_message(h_date, h_time, court, caseno, cnr, parties, stage, notes):
    return (
        f"*CHAMBER OF MADHUKUMAR MUNIRAJ, ADVOCATE*\n"
        f"*COURT HEARING REMINDER*\n\n"
        f"*Case No.:* {caseno} (CNR: {cnr})\n"
        f"*Parties:* {parties}\n"
        f"*Court / Forum:* {court}\n"
        f"*Date & Time:* {h_date} at {h_time}\n"
        f"*Stage:* {stage}\n"
        f"*Instructions:* {notes}\n\n"
        f"Kindly be present at the Court Hall 15 minutes prior to the scheduled call."
    )

def build_fee_message(matter_ref, payee, purpose, amount_inr):
    return (
        f"*CHAMBER OF MADHUKUMAR MUNIRAJ, ADVOCATE*\n"
        f"*STATUTORY COURT FEE & E-STAMP REQUISITION*\n\n"
        f"*Matter:* {matter_ref}\n"
        f"*Purpose:* {purpose}\n"
        f"*Statutory Payee:* {payee}\n"
        f"*Payable Amount:* INR {amount_inr:,.2f}\n\n"
        f"Kindly arrange for the statutory Court Fee / Digital e-Stamp remittance so the Registry filing may be completed within limitation."
    )

def seed_initial_data():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM hearings")
    if c.fetchone()[0] == 0:
        today_str = date.today().strftime("%Y-%m-%d")
        tomorrow_str = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        c.execute("""INSERT INTO hearings (hearing_date, hearing_time, court_hall, case_no, cnr_no, parties, stage, client_phone, notes)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (today_str, "10:30 AM", "CCH-83 (Commercial Court)", "Com.O.S. 125/2026", "KABN010045212026",
                   "M/s. Apex Tech v. Zenith Infra", "Arguments on I.A. No. 1 (Order XXXVIII Rule 5 CPC)", "9845000001", "Carry original invoices & Sec. 63(4) BSA certificate"))
        c.execute("""INSERT INTO hearings (hearing_date, hearing_time, court_hall, case_no, cnr_no, parties, stage, client_phone, notes)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (today_str, "02:30 PM", "XXIV ACMM Bengaluru", "C.C. 8840/2026", "KABN020112342026",
                   "Sri. Kiran Kumar v. M/s. Horizon Traders", "Cross-Examination of PW-1 (Sec. 138 NI Act)", "9845000002", "Confront witness with Ledger Extract Ex.P7"))
        c.execute("""INSERT INTO hearings (hearing_date, hearing_time, court_hall, case_no, cnr_no, parties, stage, client_phone, notes)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (tomorrow_str, "11:00 AM", "High Court of Karnataka (CH-5)", "W.P. 19420/2026", "KAHC010293842026",
                   "Harish Gowda v. State of Karnataka", "Preliminary Hearing - Interim Stay", "9845000003", "File synopsis and list of dates"))

    c.execute("SELECT COUNT(*) FROM tasks")
    if c.fetchone()[0] == 0:
        today_str = date.today().strftime("%Y-%m-%d")
        c.execute("INSERT INTO tasks (due_date, priority, category, description, status) VALUES (?, ?, ?, ?, 'PENDING')",
                  (today_str, "CRITICAL", "Filing / Registry", "Cure office objections in FR No. 4412/2026 before High Court Scrutiny Branch"))
        c.execute("INSERT INTO tasks (due_date, priority, category, description, status) VALUES (?, ?, ?, ?, 'PENDING')",
                  (today_str, "HIGH", "Drafting", "Finalize Statement of Truth & Sec. 12A PIM application for Commercial Suit"))
        c.execute("INSERT INTO tasks (due_date, priority, category, description, status) VALUES (?, ?, ?, ?, 'PENDING')",
                  (today_str, "NORMAL", "Client Conference", "Evening 06:00 PM conference with RERA complainant regarding K-RERA Form-N"))

    c.execute("SELECT COUNT(*) FROM deadlines")
    if c.fetchone()[0] == 0:
        calculate_and_add_deadline_internal(c, "Com.O.S. 125/2026", "ws_commercial", "2026-10-01")

    conn.commit()
    conn.close()

def calculate_and_add_deadline_internal(cursor, case_no, mode, trigger_date_str):
    t_date = datetime.strptime(trigger_date_str, "%Y-%m-%d").date()
    if mode == "ws_commercial":
        stat_date = t_date + timedelta(days=30)
        outer_date = t_date + timedelta(days=120)
        ref = "Order VIII Rule 1 CPC (Commercial Courts Act) - Strict 120-Day Forfeiture"
        label = "Commercial Suit Written Statement"
    elif mode == "ws_civil":
        stat_date = t_date + timedelta(days=30)
        outer_date = t_date + timedelta(days=90)
        ref = "Order VIII Rule 1 CPC (Civil) - 30 Days initial / 90 Days max"
        label = "Civil Suit Written Statement"
    elif mode == "ni138_notice":
        stat_date = t_date + timedelta(days=30)
        outer_date = t_date + timedelta(days=30)
        ref = "Sec. 138(b) NI Act - Statutory Demand Notice within 30 days of Dishonour"
        label = "NI Act Sec. 138 Demand Notice Cutoff"
    elif mode == "ni138_complaint":
        stat_date = t_date + timedelta(days=15)
        outer_date = t_date + timedelta(days=45)
        ref = "Sec. 138(c) r/w Sec. 142(1)(b) NI Act - 15 days wait + 30 days PCR filing"
        label = "NI Act Sec. 138 PCR Filing Window"
    elif mode == "sec34_arbitration":
        stat_date = t_date + timedelta(days=90)
        outer_date = t_date + timedelta(days=120)
        ref = "Sec. 34(3) Arbitration Act - 3 Months + 30 Days strict outer cap"
        label = "Sec. 34 Arbitral Award Challenge"
    else:
        stat_date = t_date + timedelta(days=30)
        outer_date = t_date + timedelta(days=60)
        ref = "General Statutory Appeal / Filing Period"
        label = "Statutory Filing Deadline"

    cursor.execute("""INSERT INTO deadlines (case_no, event_type, trigger_date, statutory_date, outer_limit_date, statute_ref)
                      VALUES (?, ?, ?, ?, ?, ?)""",
                   (case_no, label, trigger_date_str, stat_date.strftime("%Y-%m-%d"), outer_date.strftime("%Y-%m-%d"), ref))
    return label, stat_date, outer_date, ref

def calculate_and_add_deadline(case_no, mode, trigger_date_str):
    conn = get_db()
    c = conn.cursor()
    label, stat_date, outer_date, ref = calculate_and_add_deadline_internal(c, case_no, mode, trigger_date_str)
    conn.commit()
    conn.close()
    print(f"[Success] Statutory Deadline Calculated & Logged for {case_no}:")
    print(f"  -> Event            : {label}")
    print(f"  -> Trigger Date     : {trigger_date_str}")
    print(f"  -> Initial Cutoff   : {stat_date.strftime('%Y-%m-%d')}")
    print(f"  -> Strict Outer Cap : {outer_date.strftime('%Y-%m-%d')} ({ref})")
    export_ics()

def generate_client_messages():
    seed_initial_data()
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT hearing_date, hearing_time, court_hall, case_no, cnr_no, parties, stage, client_phone, notes FROM hearings ORDER BY hearing_date ASC")
    hearings = c.fetchall()
    conn.close()

    approvals = []
    agent_db_path = os.path.join("agent_workspace", "agent_state.db")
    if os.path.exists(agent_db_path):
        aconn = sqlite3.connect(agent_db_path)
        ac = aconn.cursor()
        try:
            ac.execute("SELECT id, matter_ref, payee, purpose, amount_inr, status FROM payment_approvals ORDER BY id DESC")
            approvals = ac.fetchall()
        except Exception:
            pass
        aconn.close()

    md_lines = [
        "# SWEETYAI WHATSAPP & SMS CLIENT COMMUNICATION PACKET",
        f"**Generated On:** {datetime.now().strftime('%d-%m-%Y %H:%M')}\n",
        "---",
        "## I. UPCOMING HEARING REMINDERS (WHATSAPP & SMS)\n"
    ]

    print("========================================================================================")
    print("       SWEETYAI WHATSAPP & SMS CLIENT UPDATE GENERATOR                                  ")
    print("========================================================================================")

    for h_date, h_time, court, caseno, cnr, parties, stage, phone, notes in hearings:
        msg = build_hearing_message(h_date, h_time, court, caseno, cnr, parties, stage, notes)
        clean_ph = format_indian_phone(phone)
        encoded_msg = urllib.parse.quote(msg)
        wa_url = f"https://wa.me/{clean_ph}?text={encoded_msg}" if clean_ph else f"https://wa.me/?text={encoded_msg}"
        sms_url = f"sms:+{clean_ph}?body={encoded_msg}" if clean_ph else f"sms:?body={encoded_msg}"

        print(f"\n[HEARING ALERT] {caseno} ({parties}) -> Client Phone: {phone}")
        print("-" * 88)
        print(msg)
        print(f"  -> WhatsApp Link : {wa_url[:95]}...")
        print(f"  -> SMS Link      : {sms_url[:95]}...")

        md_lines.extend([
            f"### {caseno} — {parties} ({h_date} @ {h_time})",
            f"- **Client Phone:** `{phone}`",
            f"- **[1-Tap Send via WhatsApp]({wa_url})** | **[1-Tap Send via SMS]({sms_url})**\n",
            "```text",
            msg,
            "```\n"
        ])

    if approvals:
        md_lines.append("---\n## II. COURT FEE & E-STAMP CLIENT REQUISITIONS\n")
        for tid, mref, payee, purp, amt, st in approvals:
            f_msg = build_fee_message(mref, payee, purp, amt)
            enc_f = urllib.parse.quote(f_msg)
            wa_f = f"https://wa.me/?text={enc_f}"
            sms_f = f"sms:?body={enc_f}"
            print(f"\n[COURT FEE REQUEST TX #{tid}] {mref} -> INR {amt:,.2f} [{st}]")
            print("-" * 88)
            print(f_msg)
            md_lines.extend([
                f"### TX #{tid}: {mref} (INR {amt:,.2f})",
                f"- **[1-Tap WhatsApp Fee Request]({wa_f})** | **[1-Tap SMS Fee Request]({sms_f})**\n",
                "```text",
                f_msg,
                "```\n"
            ])

    with open(CLIENT_MSG_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print("========================================================================================")
    print(f"[Success] Client WhatsApp/SMS Packet saved -> '{CLIENT_MSG_PATH}'")
    print("========================================================================================")

def export_ics():
    conn = get_db()
    c = conn.cursor()
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//SweetyAI//Advocate Legal Diary//EN",
        "CALSCALE:GREGORIAN"
    ]
    c.execute("SELECT hearing_date, hearing_time, court_hall, case_no, parties, stage FROM hearings")
    for h_date, h_time, court, caseno, parties, stage in c.fetchall():
        dt_clean = h_date.replace("-", "")
        lines.extend([
            "BEGIN:VEVENT",
            f"DTSTART;VALUE=DATE:{dt_clean}",
            f"SUMMARY:[HEARING] {caseno} - {court} ({h_time})",
            f"DESCRIPTION:Parties: {parties} | Stage: {stage}",
            "BEGIN:VALARM",
            "TRIGGER:-PT2H",
            "ACTION:DISPLAY",
            f"DESCRIPTION:Court Hearing Reminder: {caseno} at {court}",
            "END:VALARM",
            "END:VEVENT"
        ])
    c.execute("SELECT case_no, event_type, outer_limit_date, statute_ref FROM deadlines")
    for caseno, ev, out_date, ref in c.fetchall():
        dt_clean = out_date.replace("-", "")
        lines.extend([
            "BEGIN:VEVENT",
            f"DTSTART;VALUE=DATE:{dt_clean}",
            f"SUMMARY:[STATUTORY DEADLINE] {caseno} - {ev}",
            f"DESCRIPTION:Strict Statutory Cutoff under {ref}",
            "BEGIN:VALARM",
            "TRIGGER:-P1D",
            "ACTION:DISPLAY",
            f"DESCRIPTION:Statutory Limitation Alert: {caseno} ({ev})",
            "END:VALARM",
            "END:VEVENT"
        ])
    lines.append("END:VCALENDAR")
    conn.close()
    with open(ICS_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def export_html_dashboard(hearings, tasks, deadlines):
    os.makedirs("court_ready_exports", exist_ok=True)
    today_disp = date.today().strftime("%A, %d %B %Y")
    h_rows = "".join(
        f"<tr><td><b>{h[2]}</b><br><small>{h[1]}</small></td><td>{h[3]}</td><td><b>{h[4]}</b><br><small>CNR: {h[5]}</small></td><td>{h[6]}</td><td><span class='badge'>{h[7]}</span><br><small>{h[9]}</small></td></tr>"
        for h in hearings
    )
    t_rows = "".join(
        f"<tr><td>#{t[0]}</td><td><b>{t[2]}</b></td><td>{t[3]}</td><td>{t[4]}</td><td>{t[1]}</td><td>{t[5]}</td></tr>"
        for t in tasks
    )
    d_rows = "".join(
        f"<tr><td><b>{d[1]}</b></td><td>{d[2]}</td><td>{d[3]}</td><td><b>{d[4]}</b></td><td style='color:#b91c1c;font-weight:bold;'>{d[5]}</td><td><small>{d[6]}</small></td></tr>"
        for d in deadlines
    )
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>SweetyAI Advocate Daily Executive Dashboard</title>
<style>
body {{ font-family: Verdana, sans-serif; margin: 24px; background: #f8fafc; color: #0f172a; }}
.header {{ background: #1e293b; color: #fff; padding: 18px 24px; border-radius: 8px; margin-bottom: 20px; }}
.grid {{ display: grid; grid-template-columns: 1fr; gap: 20px; }}
.card {{ background: #fff; padding: 18px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 5px solid #2563eb; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
th, td {{ border: 1px solid #cbd5e1; padding: 8px 10px; text-align: left; }}
th {{ background: #f1f5f9; }}
.badge {{ background: #dbeafe; color: #1e40af; padding: 2px 6px; border-radius: 4px; font-weight: bold; }}
</style>
</head>
<body>
<div class="header">
  <h2 style="margin:0;">SWEETYAI — ADVOCATE DAILY EXECUTIVE BRIEFING & CASE DIARY</h2>
  <p style="margin:5px 0 0 0; opacity:0.85;">Date: {today_disp} | Counsel: Madhukumar Muniraj</p>
</div>
<div class="grid">
  <div class="card">
    <h3>1. Court Cause List & Scheduled Hearings</h3>
    <table>
      <tr><th>Date / Time</th><th>Court / Forum</th><th>Case & CNR No.</th><th>Parties</th><th>Stage & Brief Notes</th></tr>
      {h_rows}
    </table>
  </div>
  <div class="card" style="border-left-color:#dc2626;">
    <h3>2. Statutory Limitation & Filing Deadlines</h3>
    <table>
      <tr><th>Case No.</th><th>Event</th><th>Trigger Date</th><th>30/90d Cutoff</th><th>Strict Outer Cap</th><th>Controlling Provision</th></tr>
      {d_rows}
    </table>
  </div>
  <div class="card" style="border-left-color:#16a34a;">
    <h3>3. Prioritized Chamber To-Do List & Filings</h3>
    <table>
      <tr><th>ID</th><th>Priority</th><th>Category</th><th>Task Description</th><th>Due Date</th><th>Status</th></tr>
      {t_rows}
    </table>
  </div>
</div>
</body>
</html>"""
    with open(HTML_DASHBOARD, "w", encoding="utf-8") as f:
        f.write(html)

def show_morning_briefing(send_notify=False):
    seed_initial_data()
    conn = get_db()
    c = conn.cursor()
    today_str = date.today().strftime("%Y-%m-%d")

    c.execute("SELECT * FROM hearings ORDER BY hearing_date ASC, hearing_time ASC")
    hearings = c.fetchall()

    c.execute("SELECT * FROM tasks WHERE status='PENDING' ORDER BY CASE priority WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 ELSE 3 END")
    tasks = c.fetchall()

    c.execute("SELECT * FROM deadlines ORDER BY outer_limit_date ASC")
    deadlines = c.fetchall()
    conn.close()

    export_ics()
    export_html_dashboard(hearings, tasks, deadlines)

    print("========================================================================================")
    print(f"       SWEETYAI ADVOCATE EXECUTIVE MORNING BRIEFING — {date.today().strftime('%d-%m-%Y (%A)')}")
    print("========================================================================================")

    print("\n[I] UPCOMING COURT CAUSE LIST & ROZNAMA (DIARY):")
    print("-" * 88)
    for h in hearings:
        marker = "TODAY" if h[1] == today_str else h[1]
        print(f"  * [{marker} @ {h[2]}] {h[3]} | {h[4]} (CNR: {h[5]})")
        print(f"    Parties : {h[6]} | Stage: {h[7]}")
        print(f"    Notes   : {h[9]} (Client Contact: {h[8]})")

    print("\n[II] PRIORITIZED CHAMBER TO-DO & REGISTRY TASKS:")
    print("-" * 88)
    for t in tasks:
        print(f"  [#{t[0]}] [{t[2]}] ({t[3]}) {t[4]} [Due: {t[1]}]")

    print("\n[III] STATUTORY LIMITATION & DEADLINE WATCHLIST:")
    print("-" * 88)
    for d in deadlines:
        days_left = (datetime.strptime(d[5], "%Y-%m-%d").date() - date.today()).days
        print(f"  * {d[1]} ({d[2]}) -> Initial: {d[4]} | STRICT OUTER CAP: {d[5]} ({days_left} days left)")
        print(f"    Statute : {d[6]}")

    print("\n[IV] RECOMMENDED ADVOCATE DAILY TIME-BLOCK PLAN:")
    print("-" * 88)
    print("  08:30 AM - 10:00 AM : Chamber Reading, Brief Preparation & Case Law Verification")
    print("  10:30 AM - 01:30 PM : Morning Court Rounds (Roll Call, Interim Applications & Admissions)")
    print("  01:30 PM - 02:30 PM : Lunch & High Court / Civil Court Registry Scrutiny & Filing Check")
    print("  02:30 PM - 04:45 PM : Afternoon Session (Witness Cross-Examination & Final Arguments)")
    print("  05:30 PM - 07:30 PM : Client Conferences, Notice Drafting & Next-Day Cause List Sync")
    print("========================================================================================")
    print(f"[Sync] Mobile Calendar (.ics) saved -> '{ICS_PATH}'")
    print(f"[Sync] Executive HTML Dashboard     -> '{HTML_DASHBOARD}'")
    print("========================================================================================")

    if send_notify:
        try:
            subprocess.run(["notify-send", "-u", "critical", "SweetyAI Morning Legal Briefing", f"{len(hearings)} Court Hearings | {len(tasks)} Pending Tasks | {len(deadlines)} Statutory Deadlines"], check=False)
        except Exception:
            pass

def handle_diary_cli(args):
    seed_initial_data()
    p = argparse.ArgumentParser(prog="sweety diary")
    sub = p.add_subparsers(dest="subcmd")

    p_brief = sub.add_parser("briefing", help="Show full daily morning briefing, cause list, tasks & time-plan")
    p_brief.add_argument("--notify", action="store_true", help="Send Linux desktop notification popup")

    p_cmsg = sub.add_parser("client-notify", help="Generate WhatsApp & SMS hearing reminders and court fee messages for clients")

    p_hear = sub.add_parser("add-hearing", help="Add a court hearing to the Case Diary")
    p_hear.add_argument("--date", default=date.today().strftime("%Y-%m-%d"), help="Hearing date YYYY-MM-DD")
    p_hear.add_argument("--time", default="10:30 AM", help="Hearing time")
    p_hear.add_argument("--court", required=True, help="Court Hall / Forum (e.g., CCH-83, XXIV ACMM)")
    p_hear.add_argument("--caseno", required=True, help="Case Number")
    p_hear.add_argument("--cnr", default="KABN000000002026", help="16-digit eCourts CNR Number")
    p_hear.add_argument("--parties", required=True, help="Cause title / Parties")
    p_hear.add_argument("--stage", default="Hearing / Arguments", help="Stage of case")
    p_hear.add_argument("--phone", default="9845000001", help="Client phone number")
    p_hear.add_argument("--notes", default="Carry case file", help="Preparation notes")

    p_task = sub.add_parser("add-task", help="Add a prioritized task or reminder")
    p_task.add_argument("--desc", required=True, help="Task description")
    p_task.add_argument("--priority", choices=["CRITICAL", "HIGH", "NORMAL"], default="HIGH")
    p_task.add_argument("--category", default="Litigation", help="Task category (Filing, Drafting, Client)")
    p_task.add_argument("--due", default=date.today().strftime("%Y-%m-%d"), help="Due date YYYY-MM-DD")

    p_done = sub.add_parser("done", help="Mark a task ID as completed")
    p_done.add_argument("--id", type=int, required=True, help="Task ID number")

    p_dead = sub.add_parser("deadline", help="Auto-calculate statutory deadline and add to calendar")
    p_dead.add_argument("--caseno", required=True, help="Case number or matter name")
    p_dead.add_argument("--mode", choices=["ws_commercial", "ws_civil", "ni138_notice", "ni138_complaint", "sec34_arbitration"], required=True)
    p_dead.add_argument("--trigger-date", required=True, help="Date of summons service / dishonour / award (YYYY-MM-DD)")

    if not args or args[0] in ("show", "briefing"):
        notify_flag = "--notify" in args
        show_morning_briefing(send_notify=notify_flag)
        return

    parsed = p.parse_args(args)
    if parsed.subcmd == "client-notify":
        generate_client_messages()
    elif parsed.subcmd == "add-hearing":
        conn = get_db()
        conn.execute("""INSERT INTO hearings (hearing_date, hearing_time, court_hall, case_no, cnr_no, parties, stage, client_phone, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                     (parsed.date, parsed.time, parsed.court, parsed.caseno, parsed.cnr, parsed.parties, parsed.stage, parsed.phone, parsed.notes))
        conn.commit()
        conn.close()
        export_ics()
        print(f"[Success] Hearing added to Case Diary: {parsed.caseno} on {parsed.date} at {parsed.court}")
    elif parsed.subcmd == "add-task":
        conn = get_db()
        conn.execute("INSERT INTO tasks (due_date, priority, category, description, status) VALUES (?, ?, ?, ?, 'PENDING')",
                     (parsed.due, parsed.priority, parsed.category, parsed.desc))
        conn.commit()
        conn.close()
        print(f"[Success] Added [{parsed.priority}] Task: {parsed.desc}")
    elif parsed.subcmd == "done":
        conn = get_db()
        conn.execute("UPDATE tasks SET status='COMPLETED' WHERE id=?", (parsed.id,))
        conn.commit()
        conn.close()
        print(f"[Success] Task #{parsed.id} marked as COMPLETED!")
    elif parsed.subcmd == "deadline":
        calculate_and_add_deadline(parsed.caseno, parsed.mode, parsed.trigger_date)
    else:
        show_morning_briefing()

if __name__ == "__main__":
    handle_diary_cli(sys.argv[1:])
'''

# ==============================================================================
# 2. UPGRADE MOBILE_PORTAL.PY WITH 1-TAP WHATSAPP & SMS CLIENT BUTTONS
# ==============================================================================
MOBILE_PORTAL_V3_CODE = r'''import os
import sys
import io
import socket
import urllib.parse
import subprocess
from contextlib import redirect_stdout
from datetime import date, datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from advocate_diary import (
    get_db,
    seed_initial_data,
    export_ics,
    format_indian_phone,
    build_hearing_message,
    build_fee_message
)
from sweety_agents import (
    get_agent_db,
    seed_default_routines,
    approve_transaction,
    run_multi_bot_mission
)

def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

class SweetyMobileHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path.startswith("/download/"):
            rel_path = urllib.parse.unquote(parsed.path[len("/download/"):])
            safe_path = os.path.abspath(rel_path)
            if os.path.exists(safe_path) and os.path.isfile(safe_path):
                self.send_response(200)
                if safe_path.endswith(".ics"):
                    self.send_header("Content-Type", "text/calendar; charset=utf-8")
                elif safe_path.endswith(".html"):
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                else:
                    self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Disposition", f'attachment; filename="{os.path.basename(safe_path)}"')
                self.end_headers()
                with open(safe_path, "rb") as f:
                    self.wfile.write(f.read())
                return

        if parsed.path == "/done":
            qs = urllib.parse.parse_qs(parsed.query)
            tid = qs.get("id", [""])[0]
            if tid.isdigit():
                conn = get_db()
                conn.execute("UPDATE tasks SET status='COMPLETED' WHERE id=?", (int(tid),))
                conn.commit()
                conn.close()
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return

        if parsed.path in ("/approve_tx", "/reject_tx"):
            qs = urllib.parse.parse_qs(parsed.query)
            tx_id = qs.get("id", [""])[0]
            if tx_id.isdigit():
                is_reject = (parsed.path == "/reject_tx")
                buf = io.StringIO()
                with redirect_stdout(buf):
                    approve_transaction(int(tx_id), reject=is_reject)
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return

        self.render_dashboard("")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        params = urllib.parse.parse_qs(body)
        action = params.get("action", [""])[0]
        cmd_output = ""

        if action == "launch_mission":
            m_type = params.get("m_type", ["comm-suit"])[0]
            client = params.get("client", ["M/s. Apex Tech"])[0].strip()
            opponent = params.get("opponent", ["M/s. Zenith Corp"])[0].strip()
            try:
                amount = float(params.get("amount", ["2500000"])[0])
            except ValueError:
                amount = 2500000.0
            buf = io.StringIO()
            with redirect_stdout(buf):
                run_multi_bot_mission(m_type, client, opponent, amount)
            cmd_output = buf.getvalue()

        elif action == "add_task":
            desc = params.get("desc", [""])[0].strip()
            prio = params.get("priority", ["HIGH"])[0]
            if desc:
                conn = get_db()
                conn.execute("INSERT INTO tasks (due_date, priority, category, description, status) VALUES (?, ?, 'Mobile', ?, 'PENDING')",
                             (date.today().strftime("%Y-%m-%d"), prio, desc))
                conn.commit()
                conn.close()
                cmd_output = f"[Mobile Alert] Added [{prio}] Task: {desc}"

        elif action == "add_hearing":
            caseno = params.get("caseno", [""])[0].strip()
            court = params.get("court", ["CCH-83"])[0].strip()
            h_date = params.get("date", [date.today().strftime("%Y-%m-%d")])[0]
            h_time = params.get("time", ["10:30 AM"])[0]
            parties = params.get("parties", ["Client v. Opponent"])[0]
            stage = params.get("stage", ["Hearing"])[0]
            phone = params.get("phone", ["9845000001"])[0].strip()
            if caseno:
                conn = get_db()
                conn.execute("""INSERT INTO hearings (hearing_date, hearing_time, court_hall, case_no, cnr_no, parties, stage, client_phone, notes)
                                VALUES (?, ?, ?, ?, 'KABN000000002026', ?, ?, ?, 'Carry original documents')""",
                             (h_date, h_time, court, caseno, parties, stage, phone))
                conn.commit()
                conn.close()
                export_ics()
                cmd_output = f"[Mobile Alert] Hearing Logged: {caseno} at {court} on {h_date} (Client: {phone})"

        elif action == "run_cli":
            raw_cmd = params.get("cmd", [""])[0].strip()
            if raw_cmd:
                parts = raw_cmd.split()
                if parts[0] == "sweety":
                    parts = ["python3", "sweety.py"] + parts[1:]
                elif parts[0] != "python3":
                    parts = ["python3", "sweety.py"] + parts
                res = subprocess.run(parts, capture_output=True, text=True)
                cmd_output = res.stdout + "\n" + res.stderr

        self.render_dashboard(cmd_output)

    def render_dashboard(self, cmd_output):
        seed_initial_data()
        seed_default_routines()
        export_ics()

        conn = get_db()
        c = conn.cursor()
        today_str = date.today().strftime("%Y-%m-%d")

        c.execute("SELECT * FROM hearings ORDER BY hearing_date ASC, hearing_time ASC")
        hearings = c.fetchall()

        c.execute("SELECT * FROM tasks WHERE status='PENDING' ORDER BY CASE priority WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 ELSE 3 END")
        tasks = c.fetchall()

        c.execute("SELECT * FROM deadlines ORDER BY outer_limit_date ASC")
        deadlines = c.fetchall()
        conn.close()

        aconn = get_agent_db()
        ac = aconn.cursor()

        ac.execute("SELECT id, created_at, matter_ref, payee, purpose, amount_inr, virtual_card_label, status FROM payment_approvals ORDER BY id DESC")
        approvals = ac.fetchall()

        ac.execute("SELECT timestamp, mission_id, sender_bot, receiver_bot, action_taken, artifact_path FROM bot_messages ORDER BY id DESC LIMIT 12")
        bot_logs = list(reversed(ac.fetchall()))
        aconn.close()

        today_hearings = [h for h in hearings if h[1] == today_str]
        crit_tasks = [t for t in tasks if t[2] == "CRITICAL"]
        pending_txs = [tx for tx in approvals if tx[7] == "PENDING_HUMAN_APPROVAL"]
        alert_summary = f"{len(today_hearings)} Hearings Today | {len(pending_txs)} Pending Payments | {len(crit_tasks)} Critical Tasks"

        # 1. Render Payment Approval Queue + 1-Tap WhatsApp/SMS Fee Request Buttons
        tx_items = ""
        if not approvals:
            tx_items = "<div class='item' style='color:#94a3b8;'>No transactions queued yet.</div>"
        for tid, cat, mref, payee, purp, amt, card, st in approvals:
            fee_msg = build_fee_message(mref, payee, purp, amt)
            enc_fee = urllib.parse.quote(fee_msg)
            wa_fee_link = f"https://wa.me/?text={enc_fee}"
            sms_fee_link = f"sms:?body={enc_fee}"

            if st == "PENDING_HUMAN_APPROVAL":
                badge = "<span style='background:#f59e0b;color:#000;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>PENDING APPROVAL</span>"
                action_btns = f"""<div class='btn-row' style='margin-top:8px;'>
                    <a href='/approve_tx?id={tid}' style='background:#16a34a;color:#fff;'>Approve (INR {amt:,.0f})</a>
                    <a href='/reject_tx?id={tid}' style='background:#dc2626;color:#fff;'>Reject</a>
                </div>"""
            elif st == "APPROVED_AND_DISBURSED":
                badge = "<span style='background:#22c55e;color:#000;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>APPROVED & DISBURSED</span>"
                action_btns = ""
            else:
                badge = "<span style='background:#ef4444;color:#fff;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>REJECTED BY COUNSEL</span>"
                action_btns = ""

            client_fee_btns = f"""<div class='btn-row' style='margin-top:6px;'>
                <a href='{wa_fee_link}' target='_blank' style='background:#25D366;color:#000;'>WhatsApp Fee Request</a>
                <a href='{sms_fee_link}' style='background:#0284c7;color:#fff;'>SMS Fee Request</a>
            </div>"""

            tx_items += f"""<div class='item'>
                <div style='display:flex;justify-content:space-between;align-items:center;'>
                    <b>TX #{tid} — INR {amt:,.2f}</b> {badge}
                </div>
                <div style='color:#38bdf8;font-size:13px;font-weight:bold;margin-top:3px;'>{mref}</div>
                <div style='font-size:12px;color:#cbd5e1;'>Payee: {payee} | Card: {card}</div>
                {action_btns}
                {client_fee_btns}
            </div>"""

        # 2. Render Multi-Bot Collaboration Transcript
        bot_items = ""
        if not bot_logs:
            bot_items = "<div class='item' style='color:#94a3b8;'>No bot collaboration logs yet. Dispatch a mission below!</div>"
        for ts, mid, s_bot, r_bot, act, art in bot_logs:
            art_html = f"<div style='font-size:11px;color:#4ade80;margin-top:2px;'>Artifact: {art}</div>" if art else ""
            bot_items += f"""<div class='item' style='border-left:3px solid #38bdf8;padding-left:8px;'>
                <div style='font-size:11px;color:#94a3b8;'>[{ts}] <b style='color:#f8fafc;'>{mid}</b></div>
                <div style='font-size:13px;margin-top:2px;'><b style='color:#f59e0b;'>{s_bot}</b> &rarr; <b style='color:#38bdf8;'>{r_bot}</b></div>
                <div style='font-size:13px;color:#e2e8f0;margin-top:2px;'>{act}</div>
                {art_html}
            </div>"""

        # 3. Render Hearings + 1-Tap WhatsApp & SMS Client Reminder Buttons
        h_items = ""
        for h in hearings:
            tag = "<span style='background:#dc2626;color:#fff;padding:2px 6px;border-radius:4px;font-size:11px;'>TODAY</span>" if h[1] == today_str else f"<span style='background:#334155;color:#fff;padding:2px 6px;border-radius:4px;font-size:11px;'>{h[1]}</span>"
            h_msg = build_hearing_message(h[1], h[2], h[3], h[4], h[5], h[6], h[7], h[9])
            enc_h = urllib.parse.quote(h_msg)
            clean_ph = format_indian_phone(h[8])
            wa_h_link = f"https://wa.me/{clean_ph}?text={enc_h}" if clean_ph else f"https://wa.me/?text={enc_h}"
            sms_h_link = f"sms:+{clean_ph}?body={enc_h}" if clean_ph else f"sms:?body={enc_h}"

            h_items += f"""<div class='item'>
                <div>{tag} <b>{h[2]} — {h[3]}</b></div>
                <div style='color:#38bdf8;font-weight:bold;margin-top:3px;'>{h[4]} ({h[6]})</div>
                <div style='font-size:12px;color:#cbd5e1;'>Stage: {h[7]} | Client Phone: <b>{h[8]}</b></div>
                <div style='font-size:12px;color:#94a3b8;'>Note: {h[9]}</div>
                <div class='btn-row' style='margin-top:6px;'>
                    <a href='{wa_h_link}' target='_blank' style='background:#25D366;color:#000;'>WhatsApp Client Alert</a>
                    <a href='{sms_h_link}' style='background:#0284c7;color:#fff;'>SMS Client Reminder</a>
                </div>
            </div>"""

        # 4. Render Tasks
        t_items = ""
        for t in tasks:
            p_color = "#ef4444" if t[2] == "CRITICAL" else ("#f59e0b" if t[2] == "HIGH" else "#10b981")
            t_items += f"""<div class='item' style='display:flex;justify-content:space-between;align-items:center;'>
                <div>
                    <span style='background:{p_color};color:#fff;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>{t[2]}</span>
                    <span style='font-size:14px;margin-left:6px;'>{t[4]}</span>
                </div>
                <a href='/done?id={t[0]}' style='background:#22c55e;color:#fff;text-decoration:none;padding:5px 10px;border-radius:6px;font-size:12px;font-weight:bold;'>Done</a>
            </div>"""

        # 5. Render Deadlines
        d_items = ""
        for d in deadlines:
            days_left = (datetime.strptime(d[5], "%Y-%m-%d").date() - date.today()).days
            d_items += f"""<div class='item' style='border-left:3px solid #ef4444;padding-left:8px;'>
                <div style='font-weight:bold;color:#fca5a5;'>{d[1]} — {d[2]} ({days_left} days left)</div>
                <div style='font-size:12px;color:#cbd5e1;'>Initial: {d[4]} | Strict Outer Cap: <b>{d[5]}</b></div>
            </div>"""

        # 6. Render Downloadable Files
        files_html = ""
        folders = ["court_ready_exports", "diary_data", "commercial_suits", "family_court_petitions", "consumer_petitions", "mact_petitions", "ipr_notices", "labour_claims", "ibc_sec7_petitions", "writ_petitions", "cyber_notices", "rera_petitions", "excel_claim_schedules"]
        for folder in folders:
            if os.path.exists(folder):
                for fn in sorted(os.listdir(folder))[:5]:
                    fp = os.path.join(folder, fn)
                    if os.path.isfile(fp):
                        files_html += f"<div class='item'><a href='/download/{urllib.parse.quote(fp)}' style='color:#38bdf8;text-decoration:none;font-size:13px;'>[Download] {folder}/{fn}</a></div>"

        out_block = f"<pre style='background:#000;color:#4ade80;padding:10px;border-radius:6px;overflow-x:auto;font-size:12px;'>{cmd_output}</pre>" if cmd_output else ""

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SweetyAI Mobile Legal Hub & Client Communicator</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 12px; }}
.banner {{ background: linear-gradient(135deg, #dc2626, #991b1b); padding: 14px; border-radius: 10px; margin-bottom: 14px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
.card {{ background: #1e293b; padding: 14px; border-radius: 10px; margin-bottom: 14px; border: 1px solid #334155; }}
h3 {{ margin: 0 0 10px 0; font-size: 16px; color: #f8fafc; }}
.item {{ padding: 8px 0; border-bottom: 1px solid #334155; }}
input, select, button {{ width: 100%; padding: 10px; margin-top: 6px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: #fff; box-sizing: border-box; font-size: 14px; }}
button {{ background: #2563eb; border: none; font-weight: bold; cursor: pointer; }}
.btn-row {{ display: flex; gap: 8px; margin-top: 10px; }}
.btn-row a, .btn-row button {{ flex: 1; text-align: center; padding: 9px; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: bold; }}
</style>
<script>
function triggerMobileAlert() {{
    var msg = "{alert_summary}";
    if ("Notification" in window) {{
        Notification.requestPermission().then(function(permission) {{
            if (permission === "granted") {{
                new Notification("SweetyAI Advocate Alert", {{ body: msg }});
            }} else {{
                alert("SweetyAI Mobile Alert:\\n" + msg);
            }}
        }});
    }} else {{
        alert("SweetyAI Mobile Alert:\\n" + msg);
    }}
}}

function sendCustomClientMsg(mode) {{
    var phone = document.getElementById("c_phone").value.replace(/\\D/g, "");
    if (phone.length === 10) {{ phone = "91" + phone; }}
    var caseno = document.getElementById("c_caseno").value || "Pending Matter";
    var tpl = document.getElementById("c_tpl").value;
    var extra = document.getElementById("c_extra").value || "";
    var text = "*CHAMBER OF MADHUKUMAR MUNIRAJ, ADVOCATE*\\n";
    if (tpl === "hearing") {{
        text += "*HEARING REMINDER*\\nCase: " + caseno + "\\nKindly attend Court Hall 15 mins prior. " + extra;
    }} else if (tpl === "fee") {{
        text += "*COURT FEE / E-STAMP REQUEST*\\nCase: " + caseno + "\\nKindly remit the statutory Court Fee / e-Stamp amount for filing. " + extra;
    }} else if (tpl === "sec63") {{
        text += "*SEC. 63(4) BSA ELECTRONIC EVIDENCE REQUEST*\\nCase: " + caseno + "\\nKindly provide device details & sign the Section 63(4) BSA Certificate. " + extra;
    }} else {{
        text += "*CASE STATUS & ROZNAMA UPDATE*\\nCase: " + caseno + "\\nUpdate: " + extra;
    }}
    var encoded = encodeURIComponent(text);
    if (mode === "wa") {{
        window.open("https://wa.me/" + phone + "?text=" + encoded, "_blank");
    }} else {{
        window.location.href = "sms:+" + phone + "?body=" + encoded;
    }}
}}
</script>
</head>
<body>
<div class="banner">
  <div style="font-weight:bold;font-size:15px;">SWEETYAI LIVE MOBILE COMMAND & ALERTS</div>
  <div style="font-size:13px;margin-top:4px;">{alert_summary}</div>
  <div class="btn-row">
    <button onclick="triggerMobileAlert()" style="background:#f59e0b;color:#000;margin:0;">Test Phone Popup Alert</button>
    <a href="/download/diary_data/advocate_calendar.ics" style="background:#fff;color:#0f172a;">Sync Alarms to Phone (.ics)</a>
  </div>
</div>

{out_block}

<div class="card" style="border: 1px solid #f59e0b;">
  <h3>1. Human-in-the-Loop Payment Gate & Client Fee Requests</h3>
  {tx_items}
</div>

<div class="card" style="border: 1px solid #38bdf8;">
  <h3>2. Multi-Bot Team Collaboration Transcript</h3>
  <div style="max-height: 250px; overflow-y: auto; padding-right: 4px;">
    {bot_items}
  </div>
  <form method="POST" style="margin-top:12px; border-top:1px solid #334155; padding-top:10px;">
    <div style="font-size:13px;font-weight:bold;color:#38bdf8;margin-bottom:4px;">Dispatch New 4-Bot Mission from Phone:</div>
    <input type="hidden" name="action" value="launch_mission">
    <select name="m_type">
      <option value="comm-suit">Commercial Suit (Sec. 12A PIM + Plaint)</option>
      <option value="consumer">Consumer Protection Complaint (Sec. 35)</option>
      <option value="rera">K-RERA Builder Delay Complaint (Sec. 18)</option>
      <option value="writ">High Court Writ Petition (Art. 226)</option>
    </select>
    <input type="text" name="client" placeholder="Client / Plaintiff Name" required>
    <input type="text" name="opponent" placeholder="Opponent / Defendant Name" required>
    <input type="number" name="amount" placeholder="Claim Amount in INR (e.g. 3500000)" value="3500000" required>
    <button type="submit" style="background:#0284c7;">Launch 4-Bot Autonomous Team</button>
  </form>
</div>

<div class="card" style="border: 1px solid #25D366;">
  <h3>3. Court Cause List & 1-Tap Client Reminders</h3>
  {h_items}
  <form method="POST" style="margin-top:10px;">
    <input type="hidden" name="action" value="add_hearing">
    <input type="text" name="caseno" placeholder="Case No. (e.g. Com.O.S. 305/2026)" required>
    <input type="text" name="court" placeholder="Court Hall (e.g. CCH-83 / High Court CH-5)" required>
    <input type="text" name="parties" placeholder="Parties (e.g. Apex v. Zenith)" required>
    <input type="text" name="phone" placeholder="Client 10-Digit Mobile (e.g. 9845000001)" required>
    <input type="date" name="date" value="{today_str}">
    <button type="submit">Add Hearing & Generate Client Links</button>
  </form>
</div>

<div class="card" style="border: 1px solid #a855f7;">
  <h3>4. Instant WhatsApp / SMS Client Update Composer</h3>
  <input type="text" id="c_phone" placeholder="Client Mobile No. (e.g. 9845000001)">
  <input type="text" id="c_caseno" placeholder="Case No. / Matter (e.g. Com.O.S. 125/2026)">
  <select id="c_tpl">
    <option value="hearing">Hearing Attendance Reminder</option>
    <option value="fee">Statutory Court Fee / e-Stamp Request</option>
    <option value="sec63">Sec. 63(4) BSA Electronic Certificate Request</option>
    <option value="roznama">Daily Court Order / Next Date Update</option>
  </select>
  <input type="text" id="c_extra" placeholder="Additional Note / Amount / Next Date...">
  <div class="btn-row">
    <button type="button" onclick="sendCustomClientMsg('wa')" style="background:#25D366;color:#000;margin:0;">Send via WhatsApp</button>
    <button type="button" onclick="sendCustomClientMsg('sms')" style="background:#0284c7;color:#fff;margin:0;">Send via SMS</button>
  </div>
</div>

<div class="card">
  <h3>5. Chamber To-Do List & Reminders</h3>
  {t_items}
  <form method="POST" style="margin-top:10px;">
    <input type="hidden" name="action" value="add_task">
    <input type="text" name="desc" placeholder="New task or filing reminder..." required>
    <select name="priority">
      <option value="CRITICAL">CRITICAL PRIORITY</option>
      <option value="HIGH" selected>HIGH PRIORITY</option>
      <option value="NORMAL">NORMAL PRIORITY</option>
    </select>
    <button type="submit" style="background:#16a34a;">Add Task Reminder</button>
  </form>
</div>

<div class="card">
  <h3>6. Statutory Limitation Watchlist</h3>
  {d_items}
</div>

<div class="card">
  <h3>7. Download Court Files & Briefs</h3>
  {files_html}
</div>
</body>
</html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

def start_portal(port=8080):
    ip = get_lan_ip()
    print("=========================================================================")
    print("   SWEETYAI MOBILE HUB + 1-TAP WHATSAPP/SMS CLIENT COMMUNICATOR ACTIVE   ")
    print("=========================================================================")
    print(f" -> Open on Computer : http://127.0.0.1:{port}")
    print(f" -> Open on Mobile   : http://{ip}:{port}")
    print(" -> New Capabilities : 1-Tap WhatsApp & SMS Hearing + Court Fee Alerts   ")
    print("=========================================================================")
    server = HTTPServer(("0.0.0.0", port), SweetyMobileHandler)
    server.serve_forever()

if __name__ == "__main__":
    start_portal(8080)
'''

write_clean("advocate_diary.py", ADVOCATE_DIARY_CODE)
write_clean("mobile_portal.py", MOBILE_PORTAL_V3_CODE)

for fname in ("advocate_diary.py", "mobile_portal.py"):
    with open(fname, "rb") as f:
        compile(f.read(), fname, "exec")
print("[Compile Check] advocate_diary.py and mobile_portal.py compiled with 0 errors!")

# Test CLI WhatsApp & SMS Client Message Packet Generator
subprocess.run(["python3", "sweety.py", "diary", "client-notify"], check=True)
