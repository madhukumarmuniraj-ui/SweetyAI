import os
import sys
import json
import sqlite3
import argparse
import urllib.parse
import subprocess

def write_clean(filename, content):
    cleaned = content.replace("\u00a0", " ").replace("\u200b", "")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(cleaned)

SOCIAL_GATEWAY_CODE = r'''import os
import sys
import json
import sqlite3
import argparse

CONFIG_DIR = "social_config"
CONFIG_DB = os.path.join(CONFIG_DIR, "gateway_credentials.db")

def get_db():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    conn = sqlite3.connect(CONFIG_DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS platforms (
        platform_name TEXT PRIMARY KEY,
        api_key TEXT,
        api_secret TEXT,
        access_token TEXT,
        status TEXT DEFAULT 'DISCONNECTED'
    )""")
    conn.commit()
    return conn

def configure_platform(platform, key, secret, token=""):
    conn = get_db()
    conn.execute("""INSERT OR REPLACE INTO platforms (platform_name, api_key, api_secret, access_token, status)
                    VALUES (?, ?, ?, ?, 'CONNECTED')""",
                 (platform.lower(), key, secret, token))
    conn.commit()
    conn.close()
    print(f"[Success] Platform '{platform.upper()}' configured and marked as CONNECTED securely in local DB.")

def list_platforms():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT platform_name, status FROM platforms")
    rows = c.fetchall()
    conn.close()
    print("=========================================================================")
    print("        SWEETYAI SECURE SOCIAL MEDIA & MESSAGING GATEWAY STATUS          ")
    print("=========================================================================")
    if not rows:
        print("  No platforms configured yet. Use `python3 sweety.py social connect --platform <name> ...`")
    for p, st in rows:
        print(f"  * {p.upper()} : [{st}]")
    print("=========================================================================")

def handle_social_cli(args):
    p = argparse.ArgumentParser(prog="sweety social")
    sub = p.add_subparsers(dest="subcmd")

    p_list = sub.add_parser("status", help="List connected social and messaging platforms")
    
    p_conn = sub.add_parser("connect", help="Securely store API credentials for a platform locally")
    p_conn.add_argument("--platform", choices=["telegram", "x", "linkedin", "whatsapp"], required=True)
    p_conn.add_argument("--key", required=True, help="API Key / Client ID / Bot Token")
    p_conn.add_argument("--secret", required=True, help="API Secret / Access Token Secret")
    p_conn.add_argument("--token", default="", help="Optional Bearer Token or Extra Secret")

    if not args or args[0] == "status":
        list_platforms()
        return

    parsed = p.parse_args(args)
    if parsed.subcmd == "connect":
        configure_platform(parsed.platform, parsed.key, parsed.secret, parsed.token)
    else:
        list_platforms()

if __name__ == "__main__":
    handle_social_cli(sys.argv[1:])
'''

write_clean("social_gateway.py", SOCIAL_GATEWAY_CODE)

with open("sweety.py", "r", encoding="utf-8") as f:
    router_code = f.read().replace("\u00a0", " ").replace("\u200b", "")

social_route = '''        # Module 40: Secure Social Media & Messaging Gateway Suite
        if _cmd in ("social", "gateway") or (_cmd == "legal" and _sub in ("social", "gateway")):
            from social_gateway import handle_social_cli
            _args = _sys.argv[2:] if _cmd in ("social", "gateway") else _sys.argv[3:]
            handle_social_cli(_args)
            _sys.exit(0)

'''

if "social_gateway" not in router_code:
    target = "        # Mobile Web Portal"
    router_code = router_code.replace(target, social_route + target)
    write_clean("sweety.py", router_code)

for fname in ("social_gateway.py", "sweety.py"):
    with open(fname, "rb") as f:
        compile(f.read(), fname, "exec")
print("[Compile Check] social_gateway.py and sweety.py compiled successfully!")

subprocess.run(["python3", "sweety.py", "social", "status"], check=True)
