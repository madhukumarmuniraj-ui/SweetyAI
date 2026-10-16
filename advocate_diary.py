import os
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


def sync_to_root_db():
    """Automatically mirrors diary_data/advocate_diary.db hearings into root sweety_cases.db."""
    try:
        import sqlite3, os
        d_path = os.path.join("diary_data", "advocate_diary.db")
        if not os.path.exists(d_path):
            return
        d_conn = sqlite3.connect(d_path)
        d_cur = d_conn.cursor()
        d_cur.execute("PRAGMA table_info(hearings);")
        cols = [c[1] for c in d_cur.fetchall()]
        d_cur.execute("SELECT * FROM hearings;")
        rows = d_cur.fetchall()

        r_conn = sqlite3.connect("sweety_cases.db")
        r_cur = r_conn.cursor()
        r_cur.execute("""CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number TEXT NOT NULL,
            client_name TEXT NOT NULL,
            court TEXT NOT NULL,
            hearing_date TEXT NOT NULL,
            status TEXT NOT NULL
        )""")
        r_cur.execute("DELETE FROM cases;")
        for r in rows:
            rd = dict(zip(cols, r))
            r_cur.execute(
                "INSERT INTO cases (case_number, client_name, court, hearing_date, status) VALUES (?, ?, ?, ?, ?)",
                (
                    rd.get("case_no") or rd.get("case_number") or "Unknown",
                    rd.get("client_name") or rd.get("parties") or "Client",
                    rd.get("court") or rd.get("forum") or "Court",
                    rd.get("next_date") or rd.get("hearing_date") or "TBD",
                    rd.get("stage") or rd.get("status") or "Active"
                )
            )
        r_conn.commit()
        d_conn.close()
        r_conn.close()
    except Exception:
        pass

_orig_show_morning_briefing = show_morning_briefing
def show_morning_briefing(*args, **kwargs):
    sync_to_root_db()
    return _orig_show_morning_briefing(*args, **kwargs)
