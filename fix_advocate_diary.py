import os
import sys
import subprocess

def write_clean(filename, content):
    cleaned = content.replace("\u00a0", " ").replace("\u200b", "")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(cleaned)

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

    conn.commit()
    conn.close()

def calculate_and_add_deadline(case_no, mode, trigger_date_str):
    conn = get_db()
    c = conn.cursor()
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

    c.execute("""INSERT INTO deadlines (case_no, event_type, trigger_date, statutory_date, outer_limit_date, statute_ref)
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (case_no, label, trigger_date_str, stat_date.strftime("%Y-%m-%d"), outer_date.strftime("%Y-%m-%d"), ref))
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
    if not deadlines:
        print("  No statutory countdowns logged yet. Run `python3 sweety.py diary deadline --help` to add.")
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
            subprocess.run(["notify-send", "SweetyAI Legal Briefing", f"You have {len(hearings)} logged hearings and {len(tasks)} pending tasks."], check=False)
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

write_clean("advocate_diary.py", ADVOCATE_DIARY_CODE)

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

for fname in ("advocate_diary.py", "sweety.py"):
    with open(fname, "rb") as f:
        compile(f.read(), fname, "exec")
print("[Compile Check] advocate_diary.py and sweety.py compiled cleanly with 0 errors!")

subprocess.run(["python3", "sweety.py", "diary", "deadline", "--caseno", "Com.O.S. 125/2026", "--mode", "ws_commercial", "--trigger-date", "2026-10-01"], check=True)
subprocess.run(["python3", "sweety.py", "diary", "briefing", "--notify"], check=True)
