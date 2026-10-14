import os
import sys
import subprocess

def write_clean(filename, content):
    cleaned = content.replace("\u00a0", " ").replace("\u200b", "")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(cleaned)

# ==============================================================================
# 1. ENSURE CLEAN ADVOCATE DIARY ENGINE (SQLITE + ICS + DESKTOP NOTIFY)
# ==============================================================================
ADVOCATE_DIARY_CODE = r'''import os
import sys
import sqlite3
import argparse
import subprocess
from datetime import datetime, date, timedelta

DB_DIR = "diary_data"
DB_PATH = os.path.join(DB_DIR, "advocate_diary.db")
ICS_PATH = os.path.join(DB_DIR, "advocate_calendar.ics")
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

    p_hear = sub.add_parser("add-hearing", help="Add a court hearing to the Case Diary")
    p_hear.add_argument("--date", default=date.today().strftime("%Y-%m-%d"), help="Hearing date YYYY-MM-DD")
    p_hear.add_argument("--time", default="10:30 AM", help="Hearing time")
    p_hear.add_argument("--court", required=True, help="Court Hall / Forum (e.g., CCH-83, XXIV ACMM)")
    p_hear.add_argument("--caseno", required=True, help="Case Number")
    p_hear.add_argument("--cnr", default="KABN000000002026", help="16-digit eCourts CNR Number")
    p_hear.add_argument("--parties", required=True, help="Cause title / Parties")
    p_hear.add_argument("--stage", default="Hearing / Arguments", help="Stage of case")
    p_hear.add_argument("--phone", default="N/A", help="Client phone number")
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
    if parsed.subcmd == "add-hearing":
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
# 2. UPGRADE MOBILE PORTAL WITH LIVE PHONE NOTIFICATIONS & INTERACTIVE DIARY
# ==============================================================================
MOBILE_PORTAL_CODE = r'''import os
import sys
import socket
import urllib.parse
import subprocess
from datetime import date, datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from advocate_diary import get_db, seed_initial_data, export_ics

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

        self.render_dashboard("")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        params = urllib.parse.parse_qs(body)
        action = params.get("action", [""])[0]
        cmd_output = ""

        if action == "add_task":
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
            if caseno:
                conn = get_db()
                conn.execute("""INSERT INTO hearings (hearing_date, hearing_time, court_hall, case_no, cnr_no, parties, stage, client_phone, notes)
                                VALUES (?, ?, ?, ?, 'KABN000000002026', ?, ?, 'Mobile', 'Added via Mobile Portal')""",
                             (h_date, h_time, court, caseno, parties, stage))
                conn.commit()
                conn.close()
                export_ics()
                cmd_output = f"[Mobile Alert] Hearing Logged: {caseno} at {court} on {h_date}"
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

        today_hearings = [h for h in hearings if h[1] == today_str]
        crit_tasks = [t for t in tasks if t[2] == "CRITICAL"]
        alert_summary = f"{len(today_hearings)} Hearings Today | {len(crit_tasks)} Critical Tasks | {len(deadlines)} Statutory Deadlines"

        h_items = ""
        for h in hearings:
            tag = "<span style='background:#dc2626;color:#fff;padding:2px 6px;border-radius:4px;font-size:11px;'>TODAY</span>" if h[1] == today_str else f"<span style='background:#334155;color:#fff;padding:2px 6px;border-radius:4px;font-size:11px;'>{h[1]}</span>"
            h_items += f"""<div class='item'>
                <div>{tag} <b>{h[2]} — {h[3]}</b></div>
                <div style='color:#38bdf8;font-weight:bold;margin-top:3px;'>{h[4]} ({h[6]})</div>
                <div style='font-size:12px;color:#cbd5e1;'>Stage: {h[7]} | Note: {h[9]}</div>
            </div>"""

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

        d_items = ""
        for d in deadlines:
            days_left = (datetime.strptime(d[5], "%Y-%m-%d").date() - date.today()).days
            d_items += f"""<div class='item' style='border-left:3px solid #ef4444;padding-left:8px;'>
                <div style='font-weight:bold;color:#fca5a5;'>{d[1]} — {d[2]} ({days_left} days left)</div>
                <div style='font-size:12px;color:#cbd5e1;'>Initial: {d[4]} | Strict Outer Cap: <b>{d[5]}</b></div>
            </div>"""

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
<title>SweetyAI Mobile Legal Hub & Notifications</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 12px; }}
.banner {{ background: linear-gradient(135deg, #dc2626, #991b1b); padding: 14px; border-radius: 10px; margin-bottom: 14px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
.card {{ background: #1e293b; padding: 14px; border-radius: 10px; margin-bottom: 14px; border: 1px solid #334155; }}
h3 {{ margin: 0 0 10px 0; font-size: 16px; color: #f8fafc; }}
.item {{ padding: 8px 0; border-bottom: 1px solid #334155; }}
input, select, button {{ width: 100%; padding: 10px; margin-top: 6px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: #fff; box-sizing: border-box; font-size: 14px; }}
button {{ background: #2563eb; border: none; font-weight: bold; cursor: pointer; }}
.btn-row {{ display: flex; gap: 8px; margin-top: 10px; }}
.btn-row a, .btn-row button {{ flex: 1; text-align: center; padding: 10px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: bold; }}
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
</script>
</head>
<body>
<div class="banner">
  <div style="font-weight:bold;font-size:15px;">LIVE MOBILE LEGAL NOTIFICATION</div>
  <div style="font-size:13px;margin-top:4px;">{alert_summary}</div>
  <div class="btn-row">
    <button onclick="triggerMobileAlert()" style="background:#f59e0b;color:#000;margin:0;">Test Phone Popup Alert</button>
    <a href="/download/diary_data/advocate_calendar.ics" style="background:#fff;color:#0f172a;">Sync Alarms to Phone Calendar (.ics)</a>
  </div>
</div>

{out_block}

<div class="card">
  <h3>1. Court Cause List & Hearings</h3>
  {h_items}
  <form method="POST" style="margin-top:10px;">
    <input type="hidden" name="action" value="add_hearing">
    <input type="text" name="caseno" placeholder="Case No. (e.g. Com.O.S. 305/2026)" required>
    <input type="text" name="court" placeholder="Court Hall (e.g. CCH-83 / High Court CH-5)" required>
    <input type="text" name="parties" placeholder="Parties (e.g. Apex v. Zenith)" required>
    <input type="date" name="date" value="{today_str}">
    <button type="submit">Add Hearing & Update Phone Calendar</button>
  </form>
</div>

<div class="card">
  <h3>2. Chamber To-Do List & Reminders</h3>
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
  <h3>3. Statutory Limitation Watchlist</h3>
  {d_items}
</div>

<div class="card">
  <h3>4. Run SweetyAI Command from Phone</h3>
  <form method="POST">
    <input type="hidden" name="action" value="run_cli">
    <input type="text" name="cmd" placeholder="e.g. legal consumer --amount 500000">
    <button type="submit">Execute on Workstation</button>
  </form>
</div>

<div class="card">
  <h3>5. Download Court Files & Briefs</h3>
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
    print("   SWEETYAI MOBILE LEGAL PORTAL & LIVE NOTIFICATION HUB ACTIVE           ")
    print("=========================================================================")
    print(f" -> Open on Computer : http://127.0.0.1:{port}")
    print(f" -> Open on Mobile   : http://{ip}:{port}")
    print(" -> Tap 'Sync Alarms to Phone Calendar (.ics)' on your phone for offline alarms!")
    print("=========================================================================")
    server = HTTPServer(("0.0.0.0", port), SweetyMobileHandler)
    server.serve_forever()

if __name__ == "__main__":
    start_portal(8080)
'''

write_clean("advocate_diary.py", ADVOCATE_DIARY_CODE)
write_clean("mobile_portal.py", MOBILE_PORTAL_CODE)

with open("sweety.py", "r", encoding="utf-8") as f:
    router_code = f.read().replace("\u00a0", " ").replace("\u200b", "")

diary_route = '''        # Module 37 Pro: Advocate Case Diary, Statutory Deadlines & Daily Briefing
        if _cmd in ("diary", "calendar", "todo") or (_cmd == "legal" and _sub in ("diary", "calendar", "todo")):
            from advocate_diary import handle_diary_cli
            _args = _sys.argv[2:] if _cmd in ("diary", "calendar", "todo") else _sys.argv[3:]
            handle_diary_cli(_args)
            _sys.exit(0)

'''
if "advocate_diary" not in router_code:
    target = "        # Mobile Web Portal"
    router_code = router_code.replace(target, diary_route + target)

write_clean("sweety.py", router_code)

# Configure shell alias 'diary' in ~/.bashrc and ~/.zshrc
home_dir = os.path.expanduser("~")
alias_line = '\nalias diary="python3 ~/SweetyAI/sweety.py diary briefing --notify"\n'
for rc in (".bashrc", ".zshrc"):
    rc_path = os.path.join(home_dir, rc)
    if os.path.exists(rc_path):
        with open(rc_path, "r", encoding="utf-8") as f:
            rc_content = f.read()
        if "alias diary=" not in rc_content:
            with open(rc_path, "a", encoding="utf-8") as f:
                f.write(alias_line)

# Configure Linux Desktop Autostart Notification on Login
autostart_dir = os.path.join(home_dir, ".config", "autostart")
os.makedirs(autostart_dir, exist_ok=True)
desktop_entry = f"""[Desktop Entry]
Type=Application
Name=SweetyAI Morning Legal Briefing
Exec=/usr/bin/python3 {os.path.abspath('sweety.py')} diary briefing --notify
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Comment=Pops up daily court cause list and statutory deadlines on login
"""
write_clean(os.path.join(autostart_dir, "sweety_diary.desktop"), desktop_entry)

for fname in ("advocate_diary.py", "mobile_portal.py", "sweety.py"):
    with open(fname, "rb") as f:
        compile(f.read(), fname, "exec")
print("[Compile Check] advocate_diary.py, mobile_portal.py, and sweety.py compiled with 0 errors!")
print("[Alias & Autostart] 'diary' command alias and Linux morning login popup installed!")

subprocess.run(["python3", "sweety.py", "diary", "briefing", "--notify"], check=True)
