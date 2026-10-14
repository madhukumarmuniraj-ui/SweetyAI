import os
import sys

def write_clean(filename, content):
    cleaned = content.replace("\u00a0", " ").replace("\u200b", "")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(cleaned)

MOBILE_PORTAL_V2_CODE = r'''import os
import sys
import io
import socket
import urllib.parse
import subprocess
from contextlib import redirect_stdout
from datetime import date, datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from advocate_diary import get_db, seed_initial_data, export_ics
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

        # 1. File & Calendar (.ics / .html / .md) Download Endpoint
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

        # 2. Complete Chamber To-Do Task Endpoint
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

        # 3. 1-Tap Approve or Reject Court Fee / e-Stamp Payment Endpoint
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
        seed_default_routines()
        export_ics()

        # Fetch Diary Data
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

        # Fetch Multi-Bot & Payment Approval Data
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

        # 1. Render Payment Approval Queue
        tx_items = ""
        if not approvals:
            tx_items = "<div class='item' style='color:#94a3b8;'>No transactions queued yet.</div>"
        for tid, cat, mref, payee, purp, amt, card, st in approvals:
            if st == "PENDING_HUMAN_APPROVAL":
                badge = "<span style='background:#f59e0b;color:#000;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>PENDING APPROVAL</span>"
                action_btns = f"""<div class='btn-row' style='margin-top:8px;'>
                    <a href='/approve_tx?id={tid}' style='background:#16a34a;color:#fff;padding:8px;border-radius:6px;text-decoration:none;font-size:12px;font-weight:bold;text-align:center;flex:1;'>Approve (INR {amt:,.0f})</a>
                    <a href='/reject_tx?id={tid}' style='background:#dc2626;color:#fff;padding:8px;border-radius:6px;text-decoration:none;font-size:12px;font-weight:bold;text-align:center;flex:1;'>Reject</a>
                </div>"""
            elif st == "APPROVED_AND_DISBURSED":
                badge = "<span style='background:#22c55e;color:#000;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>APPROVED & DISBURSED</span>"
                action_btns = ""
            else:
                badge = "<span style='background:#ef4444;color:#fff;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;'>REJECTED BY COUNSEL</span>"
                action_btns = ""

            tx_items += f"""<div class='item'>
                <div style='display:flex;justify-content:space-between;align-items:center;'>
                    <b>TX #{tid} — INR {amt:,.2f}</b> {badge}
                </div>
                <div style='color:#38bdf8;font-size:13px;font-weight:bold;margin-top:3px;'>{mref}</div>
                <div style='font-size:12px;color:#cbd5e1;'>Payee: {payee} | Card: {card}</div>
                {action_btns}
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

        # 3. Render Hearings
        h_items = ""
        for h in hearings:
            tag = "<span style='background:#dc2626;color:#fff;padding:2px 6px;border-radius:4px;font-size:11px;'>TODAY</span>" if h[1] == today_str else f"<span style='background:#334155;color:#fff;padding:2px 6px;border-radius:4px;font-size:11px;'>{h[1]}</span>"
            h_items += f"""<div class='item'>
                <div>{tag} <b>{h[2]} — {h[3]}</b></div>
                <div style='color:#38bdf8;font-weight:bold;margin-top:3px;'>{h[4]} ({h[6]})</div>
                <div style='font-size:12px;color:#cbd5e1;'>Stage: {h[7]} | Note: {h[9]}</div>
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
<title>SweetyAI Mobile Legal Hub & Multi-Bot Command Center</title>
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
  <div style="font-weight:bold;font-size:15px;">SWEETYAI LIVE MOBILE COMMAND & ALERTS</div>
  <div style="font-size:13px;margin-top:4px;">{alert_summary}</div>
  <div class="btn-row">
    <button onclick="triggerMobileAlert()" style="background:#f59e0b;color:#000;margin:0;">Test Phone Popup Alert</button>
    <a href="/download/diary_data/advocate_calendar.ics" style="background:#fff;color:#0f172a;">Sync Alarms to Phone (.ics)</a>
  </div>
</div>

{out_block}

<div class="card" style="border: 1px solid #f59e0b;">
  <h3>1. Human-in-the-Loop Payment Approval Gate</h3>
  {tx_items}
</div>

<div class="card" style="border: 1px solid #38bdf8;">
  <h3>2. Multi-Bot Team Collaboration Transcript</h3>
  <div style="max-height: 280px; overflow-y: auto; padding-right: 4px;">
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

<div class="card">
  <h3>3. Court Cause List & Hearings</h3>
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
  <h3>4. Chamber To-Do List & Reminders</h3>
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
  <h3>5. Statutory Limitation Watchlist</h3>
  {d_items}
</div>

<div class="card">
  <h3>6. Run SweetyAI CLI Command from Phone</h3>
  <form method="POST">
    <input type="hidden" name="action" value="run_cli">
    <input type="text" name="cmd" placeholder="e.g. agents status">
    <button type="submit">Execute on Workstation</button>
  </form>
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
    print("   SWEETYAI MOBILE LEGAL HUB & MULTI-BOT APPROVAL PORTAL ACTIVE          ")
    print("=========================================================================")
    print(f" -> Open on Computer : http://127.0.0.1:{port}")
    print(f" -> Open on Mobile   : http://{ip}:{port}")
    print(" -> Features Active  : 1-Tap Court Fee Approval | Live 4-Bot Transcript  ")
    print("=========================================================================")
    server = HTTPServer(("0.0.0.0", port), SweetyMobileHandler)
    server.serve_forever()

if __name__ == "__main__":
    start_portal(8080)
'''

write_clean("mobile_portal.py", MOBILE_PORTAL_V2_CODE)

with open("mobile_portal.py", "rb") as f:
    compile(f.read(), "mobile_portal.py", "exec")
print("[Compile Check] mobile_portal.py upgraded and compiled with 0 errors!")

# Verify database linkage for both Bot Transcript and Payment Approval Queue
from sweety_agents import get_agent_db
conn = get_agent_db()
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM bot_messages")
msg_count = c.fetchone()[0]
c.execute("SELECT id, matter_ref, amount_inr, status FROM payment_approvals")
tx_rows = c.fetchall()
conn.close()

print(f"[Portal Verification] Loaded {msg_count} Multi-Bot transcript messages into Mobile UI.")
for r in tx_rows:
    print(f"[Portal Verification] Payment Gate Ready -> TX #{r[0]}: {r[1]} (INR {r[2]:,.2f}) [{r[3]}]")
