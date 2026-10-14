import os
import sys
import socket

def write_clean(filename, content):
    cleaned = content.replace("\u00a0", " ").replace("\u200b", "")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(cleaned)

# ==============================================================================
# MODULE 27: SWEETYAI INTERACTIVE MOBILE & DESKTOP WEB PORTAL (PORT 8080)
# ==============================================================================
MOBILE_PORTAL_CODE = '''from sandbox_guard import activate_home_sandbox as _activate_home_sandbox
_activate_home_sandbox()

import os
import sys
import socket
import shlex
import urllib.parse
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8080

PRESET_COMMANDS = [
    ("Full Case Packet (--latest)", "legal full-audit --latest --jurisdiction crlp"),
    ("Contract Review (--latest)", "legal review --latest"),
    ("Sec. 63(4) BSA Certificate", 'legal sec63-cert sample_contract.txt --deponent "Madhukumar Muniraj"'),
    ("Word .DOCX Track-Changes", "legal docx-redline sample_contract.txt modified_contract.txt"),
    ("Excel .XLSX Claim Schedule", "legal claim-xlsx --principal 2500000 --rate 18 --start-date 2025-01-15 --regime sec34_cpc"),
    ("Karnataka Stamp Duty & Penalty", "legal stamp-duty --instrument conveyance_urban --value 7500000 --deficit 100000"),
    ("Anticipatory Bail (Sec. 482 BNSS)", 'legal bail --type 482 --forum hc --crime-no "Crime 215/2026"'),
    ("NI Act Sec. 138 Complaint", "legal ni138 --cheque-no 884512 --amount 1500000 --cheque-date 2026-06-01 --return-date 2026-07-10 --notice-date 2026-07-20"),
    ("Criminal Appeal (Sec. 415/430 BNSS)", 'legal crl-appeal --cc-no "C.C. No. 18450/2024" --judgment-date 2026-09-25 --fine 1500000'),
    ("IBC Sec. 8 & 9 NCLT Suite", "legal ibc --principal 11500000 --rate 18 --default-date 2025-11-10"),
    ("Arbitration Sec. 21/9/11 Suite", "legal arbitration --contract-date 2024-06-15 --claim-amount 4500000 --default-date 2025-12-01"),
    ("HC Sec. 528 BNSS Quashing", 'legal hc-quash --crime-no "Crime No. 312/2026" --fir-date 2026-08-14'),
    ("Commercial Suit & Sec. 12A PIM", "legal comm-suit --principal 3800000 --rate 18 --cause-date 2025-10-01"),
    ("Order XXI CPC Execution Suite", 'legal execution --case-no "A.C. 88/2025" --decree-date 2026-03-10 --amount 4200000 --arbitral-award'),
    ("MSME Sec. 18 & 3x RBI Interest", "legal msme --acceptance-date 2025-11-01 --principal 2800000"),
]

OUTPUT_FOLDERS = [
    "word_docx_exports", "excel_claim_schedules", "court_ready_exports",
    "master_case_dossiers", "sec63_certificates", "bail_petitions",
    "ni138_complaints", "stamp_duty_reports", "criminal_appeals",
    "ibc_nclt_petitions", "arbitration_petitions", "hc_quashing_petitions",
    "commercial_suits", "execution_petitions", "msme_samadhaan_petitions",
    "contract_review_reports", "valuation_slips"
]

def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

class SweetyMobileHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self.render_dashboard()
        elif parsed.path == "/run":
            qs = urllib.parse.parse_qs(parsed.query)
            cmd_str = qs.get("cmd", [""])[0].strip()
            output_text = ""
            if cmd_str:
                args = ["python3", "sweety.py"] + shlex.split(cmd_str)
                proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                output_text = proc.stdout
            self.render_dashboard(cmd_str, output_text)
        else:
            super().do_GET()

    def render_dashboard(self, last_cmd="", cmd_output=""):
        ip = get_lan_ip()
        preset_buttons = ""
        for label, c in PRESET_COMMANDS:
            q = urllib.parse.quote(c)
            preset_buttons += f'<a class="btn" href="/run?cmd={q}">{label}</a>'

        files_html = ""
        for folder in OUTPUT_FOLDERS:
            if os.path.isdir(folder):
                items = sorted(os.listdir(folder), reverse=True)
                for fn in items[:5]:
                    rel = f"{folder}/{fn}"
                    href = urllib.parse.quote(rel)
                    files_html += f'<li><a href="/{href}" target="_blank"><b>[{folder}]</b> {fn}</a></li>'

        out_block = ""
        if cmd_output:
            safe_out = cmd_output.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            out_block = f'<h3>Command Output (`python3 sweety.py {last_cmd}`):</h3><pre>{safe_out}</pre>'

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SweetyAI Mobile Legal Workstation</title>
<style>
  body {{ font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 14px; background: #0f172a; color: #f8fafc; }}
  h1 {{ font-size: 1.25rem; margin-bottom: 4px; color: #38bdf8; }}
  .sub {{ font-size: 0.85rem; color: #94a3b8; margin-bottom: 14px; }}
  .card {{ background: #1e293b; border-radius: 10px; padding: 14px; margin-bottom: 14px; border: 1px solid #334155; }}
  input[type=text] {{ width: 100%; box-sizing: border-box; padding: 10px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: #fff; font-family: monospace; margin-bottom: 8px; }}
  button {{ width: 100%; padding: 11px; background: #0284c7; color: #fff; border: none; border-radius: 6px; font-weight: 600; font-size: 0.95rem; cursor: pointer; }}
  .grid {{ display: grid; grid-template-columns: 1fr; gap: 8px; }}
  .btn {{ display: block; padding: 10px 12px; background: #334155; color: #e2e8f0; text-decoration: none; border-radius: 6px; font-size: 0.88rem; font-weight: 500; border-left: 4px solid #38bdf8; }}
  pre {{ background: #020617; color: #a7f3d0; padding: 12px; border-radius: 8px; overflow-x: auto; font-size: 0.8rem; white-space: pre-wrap; }}
  ul {{ padding-left: 18px; margin: 0; }}
  li {{ margin-bottom: 8px; font-size: 0.88rem; }}
  li a {{ color: #7dd3fc; text-decoration: none; word-break: break-all; }}
</style>
</head>
<body>
  <h1>SweetyAI Enterprise Legal Workstation</h1>
  <div class="sub">Air-Gapped LAN Mobile Portal | Host IP: <b>http://{ip}:{PORT}</b> | Sandbox: <code>/home/madhukumarm</code></div>

  <div class="card">
    <form action="/run" method="get">
      <input type="text" name="cmd" value="{last_cmd or 'legal full-audit --latest --jurisdiction crlp'}" placeholder="Enter sweety.py args, e.g. legal review --latest">
      <button type="submit">Execute Legal Command on Workstation</button>
    </form>
    {out_block}
  </div>

  <div class="card">
    <h3 style="margin-top:0">1-Tap Mobile Legal Engines (27 Modules)</h3>
    <div class="grid">{preset_buttons}</div>
  </div>

  <div class="card">
    <h3 style="margin-top:0">Generated Court Files (Tap to View / Download to Phone)</h3>
    <ul>{files_html or '<li>No generated files yet. Tap any button above!</li>'}</ul>
  </div>
</body>
</html>"""
        encoded = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

def start_portal(port=PORT):
    ip = get_lan_ip()
    print("\\n=========================================================================")
    print("   SWEETYAI MOBILE & DESKTOP WEB PORTAL ACTIVE (SANDBOXED TO HOME)       ")
    print("=========================================================================")
    print(f"1. Connect your mobile phone to the SAME Wi-Fi network as this PC.")
    print(f"2. Open Chrome / Safari on your phone and type this exact address:")
    print(f"\\n   >>>   http://{ip}:{port}   <<<\\n")
    print("3. Press Ctrl+C in this terminal anytime to stop the mobile server.")
    print("=========================================================================\\n")
    server = HTTPServer(("0.0.0.0", port), SweetyMobileHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\n[SweetyAI] Mobile Portal stopped cleanly.")

if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else PORT
    start_portal(p)
'''

write_clean("mobile_portal.py", MOBILE_PORTAL_CODE)

# Wire `python3 sweety.py mobile` into sweety.py
with open("sweety.py", "r", encoding="utf-8") as f:
    sweety_code = f.read()

mobile_hook = '''        # Module 27: Interactive Mobile & Desktop Web Portal
        if _cmd in ("mobile", "web", "server") or (_cmd == "legal" and _sub in ("mobile", "web", "server")):
            from mobile_portal import start_portal
            start_portal(8080)
            _sys.exit(0)

'''

if "from mobile_portal import start_portal" not in sweety_code:
    target = '        # Module 16: Full Master Case Packet Pipeline'
    sweety_code = sweety_code.replace(target, mobile_hook + target)
    write_clean("sweety.py", sweety_code)

with open("mobile_portal.py", "rb") as f:
    compile(f.read(), "mobile_portal.py", "exec")
with open("sweety.py", "rb") as f:
    compile(f.read(), "sweety.py", "exec")

ip_addr = "127.0.0.1"
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("10.255.255.255", 1))
    ip_addr = s.getsockname()[0]
    s.close()
except Exception:
    pass

print("[Success] Module 27 (mobile_portal.py) installed and wired into sweety.py!")
print(f"\n>>> YOUR WORKSTATION WI-FI IP URL FOR MOBILE IS:  http://{ip_addr}:8080  <<<")
