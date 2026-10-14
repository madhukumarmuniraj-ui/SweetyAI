import os
import sys
import time
import json
import signal
import subprocess
import datetime
import requests

BASE_URL = "http://127.0.0.1:8765"
INBOX_DIR = "legal_inbox"
STATE_FILE = "sweety_daemon_state.json"
LOG_FILE = "sweety_proactive_daemon.log"
PID_FILE = "sweety_proactive_daemon.pid"
DIGEST_FILE = "PROACTIVE_AGENT_DIGEST.md"


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"ingested_files": [], "cycles_completed": 0, "last_run": None, "server_restarts": 0}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def log_event(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [24/7-Agent] {msg}"
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    return line


def ensure_inbox_and_seed():
    os.makedirs(INBOX_DIR, exist_ok=True)
    seed_file = os.path.join(INBOX_DIR, "sc_arnesh_kumar_41a_crpc.txt")
    if not os.listdir(INBOX_DIR) and not os.path.exists(seed_file):
        with open(seed_file, "w") as f:
            f.write(
                "Arnesh Kumar v. State of Bihar (2014) 8 SCC 273: The Supreme Court mandated strict compliance "
                "with Section 41 and Section 41A of the CrPC (now Section 35 BNSS) before arresting an accused "
                "for offences punishable with imprisonment up to 7 years. Police officers must issue a notice "
                "of appearance under Section 41A instead of automatic arrest."
            )


def check_and_heal_rag_server(state):
    try:
        r = requests.get(f"{BASE_URL}/", timeout=3)
        if r.status_code < 500:
            return True, "RAG Server Online (127.0.0.1:8765)"
    except Exception:
        pass

    # Self-heal: restart server.py in background using venv python if available
    py_bin = "./venv/bin/python3" if os.path.exists("./venv/bin/python3") else sys.executable
    subprocess.Popen(
        f"nohup {py_bin} server.py >> sweety_server.log 2>&1 &",
        shell=True,
        preexec_fn=os.setsid,
    )
    time.sleep(2)
    state["server_restarts"] = state.get("server_restarts", 0) + 1
    return False, "RAG Server was down -> Autonomously restarted on 127.0.0.1:8765"


def scan_and_ingest_inbox(state):
    ensure_inbox_and_seed()
    ingested_now = []
    for fname in sorted(os.listdir(INBOX_DIR)):
        if fname in state["ingested_files"] or fname.startswith("."):
            continue
        fpath = os.path.join(INBOX_DIR, fname)
        if not os.path.isfile(fpath):
            continue

        text_content = ""
        if fname.endswith((".txt", ".md")):
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                text_content = f.read().strip()
        elif fname.endswith(".pdf"):
            try:
                import pymupdf
                doc = pymupdf.open(fpath)
                text_content = "\n".join(page.get_text("text") for page in doc).strip()
            except Exception as e:
                log_event(f"PDF parse warning on {fname}: {e}")

        if text_content:
            doc_id = f"auto-{fname.replace('.', '-')}"
            try:
                resp = requests.post(
                    f"{BASE_URL}/ingest",
                    json={
                        "doc_id": doc_id,
                        "text": text_content[:4000],
                        "source": f"24/7 Auto-Ingest ({fname})",
                    },
                    timeout=5,
                )
                if resp.status_code == 200:
                    state["ingested_files"].append(fname)
                    ingested_now.append((fname, doc_id))
                    log_event(f"Autonomously ingested '{fname}' as '{doc_id}'")
            except Exception as e:
                log_event(f"Ingest deferred for '{fname}': {e}")
    return ingested_now


def update_proactive_digest(state, server_msg, newly_ingested):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    digest = (
        "# SWEETYAI 24/7 PROACTIVE AGENT DIGEST\n\n"
        f"**Last Autonomous Sweep:** {now_str}\n"
        f"**Total Background Cycles:** {state['cycles_completed']}\n"
        f"**RAG Server Watchdog:** {server_msg}\n"
        f"**Total Auto-Indexed Legal Files:** {len(state['ingested_files'])}\n\n"
        "### Recently Auto-Indexed Legal Documents (`./legal_inbox`)\n"
    )
    for f in state["ingested_files"][-10:]:
        digest += f"- `{f}` (Indexed into ChromaDB for instant RAG retrieval)\n"

    digest += (
        "\n### Standing Proactive Monitors Active (While Logged Off / Away)\n"
        "1. **Legal Inbox Auto-Ingest:** Watching `./legal_inbox/` for new judgments, FIRs, and notes.\n"
        "2. **RAG Daemon Self-Healing:** Keeping `127.0.0.1:8765` alive 24/7.\n"
        "3. **Pre-Briefing Readiness:** All newly dropped files are immediately searchable via `sweety legal query`.\n"
    )
    with open(DIGEST_FILE, "w") as f:
        f.write(digest)


def run_single_cycle(verbose=True):
    state = load_state()
    state["cycles_completed"] += 1
    state["last_run"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ok, server_msg = check_and_heal_rag_server(state)
    log_event(server_msg)

    newly_ingested = scan_and_ingest_inbox(state)
    update_proactive_digest(state, server_msg, newly_ingested)
    save_state(state)

    if verbose:
        print("\n=== SweetyAI 24/7 Proactive Autonomous Agent Suite ===")
        print(f"Cycle #          : {state['cycles_completed']} ({state['last_run']})")
        print(f"Watchdog Agent   : {server_msg}")
        print(f"Inbox Agent      : Scanned './{INBOX_DIR}' -> {len(newly_ingested)} new file(s) auto-ingested")
        for fname, doc_id in newly_ingested:
            print(f"  + Indexed      : {fname} (doc_id: {doc_id})")
        print(f"Total Indexed    : {len(state['ingested_files'])} file(s) in vector store")
        print(f"Proactive Digest : Updated '{DIGEST_FILE}'")
        print("======================================================\n")


def daemon_loop(interval=30):
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    log_event(f"24/7 Proactive Daemon started (PID {os.getpid()}, interval={interval}s)")
    while True:
        try:
            run_single_cycle(verbose=False)
        except Exception as e:
            log_event(f"Cycle error: {e}")
        time.sleep(interval)


def start_daemon():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                old_pid = int(f.read().strip())
            os.kill(old_pid, 0)
            print(f"\n[24/7 Daemon] Already running in background (PID {old_pid}).")
            run_single_cycle(verbose=True)
            return
        except Exception:
            pass

    # Run one immediate visible sweep first
    run_single_cycle(verbose=True)

    # Spawn detached background daemon immune to logoff/SIGHUP
    py_bin = "./venv/bin/python3" if os.path.exists("./venv/bin/python3") else sys.executable
    proc = subprocess.Popen(
        [py_bin, "daemon_agent.py", "--worker"],
        stdout=open(LOG_FILE, "a"),
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid,
    )
    with open(PID_FILE, "w") as f:
        f.write(str(proc.pid))
    print(f"[Success] 24/7 Proactive Background Agent is now running independently (PID {proc.pid})!")
    print(f"          It will continue working even when you close the terminal or log off.\n")


def stop_daemon():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            os.kill(pid, signal.SIGTERM)
            os.remove(PID_FILE)
            print(f"\n[24/7 Daemon] Stopped background process PID {pid}.\n")
            return
        except Exception as e:
            os.remove(PID_FILE)
            print(f"\n[24/7 Daemon] Cleaned stale PID file ({e}).\n")
            return
    print("\n[24/7 Daemon] Not currently running.\n")


def status_daemon():
    running = False
    pid = None
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            running = True
        except Exception:
            running = False

    state = load_state()
    print("\n=== SweetyAI 24/7 Always-On Daemon Status ===")
    print(f"Daemon Status    : {'ONLINE (Active in Background)' if running else 'STOPPED'}")
    if pid and running:
        print(f"Background PID   : {pid} (SIGHUP-immune / persists after logoff)")
    print(f"Cycles Completed : {state['cycles_completed']}")
    print(f"Last Sweep       : {state['last_run']}")
    print(f"Auto-Ingested    : {len(state['ingested_files'])} document(s) ({', '.join(state['ingested_files'])})")
    print(f"Digest File      : {DIGEST_FILE}")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()[-5:]
        print("\nRecent Autonomous Activity Log:")
        for l in lines:
            print("  " + l.strip())
    print("=============================================\n")


if __name__ == "__main__":
    if "--worker" in sys.argv:
        daemon_loop(30)
