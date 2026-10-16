#!/home/madhukumarm/SweetyAI/venv/bin/python3
import sys
import os
import re
import time
import sqlite3
import importlib
import subprocess
from datetime import datetime

BASE_DIR = "/home/madhukumarm/SweetyAI"
os.chdir(BASE_DIR)

WORKSPACE_PATHS = [
    BASE_DIR,
    os.path.join(BASE_DIR, "SweetyAI-Core"),
    os.path.join(BASE_DIR, "src"),
    os.path.join(BASE_DIR, "srcm"),
    os.path.join(BASE_DIR, "tools"),
]
for venv_dir in ["venv", ".venv"]:
    lib_root = os.path.join(BASE_DIR, venv_dir, "lib")
    if os.path.exists(lib_root):
        for py_ver in os.listdir(lib_root):
            site_pkgs = os.path.join(lib_root, py_ver, "site-packages")
            if os.path.exists(site_pkgs):
                WORKSPACE_PATHS.append(site_pkgs)

for p in reversed(WORKSPACE_PATHS):
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

from sweety_core import SweetyBrain


class SweetySelfHealer:
    @staticmethod
    def ensure_package(pkg_name: str, import_name: str = None):
        mod_to_load = import_name or pkg_name
        try:
            return importlib.import_module(mod_to_load)
        except ImportError:
            pip_bin = os.path.join(BASE_DIR, "venv", "bin", "pip")
            if os.path.exists(pip_bin):
                subprocess.run([pip_bin, "install", "--quiet", pkg_name], check=False)
            return importlib.import_module(mod_to_load)

    @staticmethod
    def ensure_system():
        try:
            conn = sqlite3.connect(os.path.join(BASE_DIR, "sweety_cases.db"))
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_number TEXT, client_name TEXT, court TEXT,
                    hearing_date TEXT, stage TEXT DEFAULT 'Active',
                    status TEXT DEFAULT 'Pending', notes TEXT
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ingested_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT, filepath TEXT, char_length INTEGER,
                    content TEXT, ingested_at TEXT
                )
            """)
            conn.commit()
            conn.close()

            res = subprocess.run(["systemctl", "--user", "is-active", "sweetyai.service"], capture_output=True, text=True)
            if res.stdout.strip() != "active":
                subprocess.run(["systemctl", "--user", "start", "sweetyai.service"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass


SWEETY_ENGINES = [
    (["bail", "480", "482", "483", "437", "438", "439", "anticipatory", "regular bail", "custody"], "bail_petition_generator", "bail_petitions"),
    (["quash", "writ", "528", "482 crpc", "226", "227", "mandamus", "certiorari"], "hc_quashing_writ_engine", "hc_quashing_petitions"),
    (["138", "cheque", "dishonour", "ni act", "pcr", "demand notice"], "ni138_engine", "ni138_complaints"),
    (["arbitrat", "sec 9", "sec 11", "sec 34", "conciliat", "award"], "arbitration_engine", "arbitration_petitions"),
    (["ibc", "nclt", "insolvency", "sec 7", "sec 9", "cirp", "creditor"], "ibc_engine", "ibc_nclt_petitions"),
    (["commercial suit", "com.o.s", "commercial court", "summary suit"], "commercial_suit_engine", "commercial_suits"),
    (["consumer", "mact", "motor accident", "labour", "workmen", "gratuity"], "consumer_motor_labour_engine", "consumer_petitions"),
    (["criminal appeal", "crl.a", "389", "430 bnss", "suspension of sentence", "conviction"], "crl_appeal_engine", "criminal_appeals"),
    (["rera", "cyber", "ipr", "trademark", "copyright", "defamation"], "advanced_litigation_engines", "rera_petitions"),
    (["redline", "compare contract", "diff contract"], "redline_generator", "redline_outputs"),
    (["nda", "playbook", "privacy audit", "dpdp"], "privacy_and_playbook_engine", "privacy_audit_reports"),
    (["contract", "agreement", "clause", "indemnity", "review contract"], "contract_reviewer", "contract_review_reports"),
    (["stamp duty", "conveyance", "gift deed stamp", "sale deed", "karnataka stamp"], "stamp_duty_calculator", "stamp_duty_reports"),
    (["court fee", "valuation", "kcf", "ad valorem", "limitation", "suit value"], "court_fee_calculator", "valuation_slips"),
    (["chronology", "list of dates", "synopsis", "timeline extract"], "chronology_extractor", "chronology_outputs"),
    (["cross exam", "sec 63", "65b", "electronic evidence", "witness", "contradiction"], "trial_and_evidence_suite", "cross_examination_matrices"),
    (["trial advocacy", "argument", "issues", "framing of charges"], "trial_advocacy_engine", "trial_practice_outputs"),
    (["citation", "overruled", "verify judgment", "scc", "air"], "citation_verifier", "citation_audit_reports"),
    (["fir audit", "defect", "charge sheet", "dossier", "full audit"], "full_audit_pipeline", "master_case_dossiers"),
    (["audit litigation", "case risk", "risk assessment"], "litigation_auditor", "risk_assessment_reports"),
    (["vakalath", "process memo", "index sheet", "affidavit", "filing form", "memo of appearance"], "filing_forms", "filing_forms"),
    (["pleading", "plaint", "written statement", "interlocutory", "ia draft", "order 39"], "pleading_drafter", "court_pleadings"),
    (["draft notice", "legal notice", "rejoinder", "reply notice"], "litigation_drafter", "drafts"),
    (["export", "docx", "word", "html export", "court ready"], "document_exporter", "court_ready_exports"),
    (["diary", "cause list", "hearing", "briefing", "tomorrow", "today cases", "alert", "notify"], "advocate_diary", "diary_data"),
    (["parallel precedent", "matching judgment", "similar case"], "parallel_precedent", "parallel_precedent_outputs"),
    (["skill", "firm skill", "anthropic", "practice package"], "anthropic_legal_skills_suite", "firm_skills"),
    (["boost", "workflow boost"], "anthropic_boost_engine", "swarm_outputs"),
    (["orchestrat", "multi agent", "swarm"], "orchestrator_agent", "workspace_orchestrations"),
    (["pipeline", "automate pipeline"], "pipeline_agent", "operational_pipelines"),
    (["code", "fix script", "debug", "devtool", "program"], "devtools_agent", "agent_workspace"),
    (["vision", "screen", "snapshot", "desktop", "cua"], "sweety_cua", "vision_logs"),
    (["ocr", "scan", "image text"], "docket_ocr", "vision_logs"),
    (["parse docket", "order parse"], "docket_parser", "drafts"),
    (["batch ingest", "ingest folder"], "batch_ingestor", "precedents"),
    (["monitor", "watch"], "legal_monitor", "diary_data"),
]


def sweety_call_module(mod_name: str, user_input: str, out_dir: str = "") -> str:
    script_path = os.path.join(BASE_DIR, f"{mod_name}.py")
    if not os.path.exists(script_path):
        return f"[!] Module `{mod_name}.py` not found."

    out_folder = os.path.join(BASE_DIR, out_dir) if out_dir else None
    before_files = set()
    if out_folder and os.path.exists(out_folder):
        before_files = {os.path.join(out_folder, f) for f in os.listdir(out_folder)}

    start_ts = time.time()
    outputs = []

    try:
        proc = subprocess.run(
            [sys.executable, script_path, user_input],
            cwd=BASE_DIR, input="\n\n\n", capture_output=True, text=True, timeout=45
        )
        if proc.stdout and proc.stdout.strip():
            outputs.append(proc.stdout.strip())
        if proc.returncode != 0 and proc.stderr:
            m = re.search(r"No module named '([^']+)'", proc.stderr)
            if m:
                SweetySelfHealer.ensure_package(m.group(1))
                proc2 = subprocess.run(
                    [sys.executable, script_path, user_input],
                    cwd=BASE_DIR, input="\n\n\n", capture_output=True, text=True, timeout=45
                )
                if proc2.stdout and proc2.stdout.strip():
                    outputs.append(proc2.stdout.strip())
    except Exception as e:
        outputs.append(f"[*] Execution note: {e}")

    if out_folder and os.path.exists(out_folder):
        after_files = [
            os.path.join(out_folder, f) for f in os.listdir(out_folder)
            if os.path.isfile(os.path.join(out_folder, f))
        ]
        updated = [f for f in after_files if f not in before_files or os.path.getmtime(f) >= start_ts - 2]
        if not updated and after_files:
            updated = [max(after_files, key=os.path.getmtime)]

        for uf in updated[:2]:
            if uf.endswith((".txt", ".md", ".json", ".html")):
                try:
                    with open(uf, "r", encoding="utf-8", errors="ignore") as f:
                        body = f.read().strip()
                    outputs.append(f"\n[Generated File: `{os.path.relpath(uf, BASE_DIR)}`]\n" + ("-" * 65) + "\n" + body[:3500])
                except Exception:
                    pass

    return "\n\n".join([o for o in outputs if o])


def sweety_read_document(user_input: str):
    SweetySelfHealer.ensure_package("pypdf")
    from pypdf import PdfReader

    search_dirs = [
        os.path.expanduser("~/Downloads"),
        os.path.join(BASE_DIR, "system_downloads"),
        os.path.join(BASE_DIR, "legal_inbox"),
        BASE_DIR
    ]

    pdf_path = None
    for word in user_input.split():
        clean = word.strip("'\".,;")
        if os.path.exists(clean) and os.path.isfile(clean):
            pdf_path = os.path.abspath(clean)
            break
        if clean.lower().endswith(".pdf") or len(clean) >= 16:
            for d in search_dirs:
                if os.path.exists(d):
                    cand = os.path.join(d, clean)
                    if os.path.exists(cand):
                        pdf_path = cand
                        break
                    if not clean.lower().endswith(".pdf") and os.path.exists(cand + ".pdf"):
                        pdf_path = cand + ".pdf"
                        break
        if pdf_path:
            break

    if not pdf_path:
        dl = os.path.expanduser("~/Downloads")
        if os.path.exists(dl):
            pdfs = [os.path.join(dl, f) for f in os.listdir(dl) if f.lower().endswith(".pdf")]
            if pdfs:
                pdf_path = max(pdfs, key=os.path.getmtime)

    if not pdf_path or not os.path.exists(pdf_path):
        return None, ""

    reader = PdfReader(pdf_path)
    pages = []
    for idx, page in enumerate(reader.pages, 1):
        t = page.extract_text()
        if t and t.strip():
            pages.append(f"--- [Page {idx} of {len(reader.pages)}] ---\n{t.strip()}")
    full_text = "\n\n".join(pages)

    os.makedirs(os.path.join(BASE_DIR, "precedents"), exist_ok=True)
    base_name = os.path.basename(pdf_path)
    saved_txt = os.path.join(BASE_DIR, "precedents", f"ingested_{base_name}.txt")
    with open(saved_txt, "w", encoding="utf-8") as f:
        f.write(full_text)

    try:
        conn = sqlite3.connect(os.path.join(BASE_DIR, "sweety_cases.db"))
        cur = conn.cursor()
        cur.execute("DELETE FROM ingested_documents WHERE filename = ?", (base_name,))
        cur.execute(
            "INSERT INTO ingested_documents (filename, filepath, char_length, content, ingested_at) VALUES (?, ?, ?, ?, ?)",
            (base_name, pdf_path, len(full_text), full_text, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

    try:
        import chromadb
        client = chromadb.PersistentClient(path=os.path.join(BASE_DIR, "chroma_db"))
        col = client.get_or_create_collection(name="sweety_legal_knowledge")
        col.upsert(documents=[full_text[:8000]], ids=[base_name], metadatas=[{"source": base_name}])
    except Exception:
        pass

    return pdf_path, full_text


def search_relevant_rag_only(query: str) -> str:
    """Searches local knowledge base ONLY when meaningful legal/case keywords exist."""
    stop_words = {
        "how", "are", "you", "who", "what", "when", "where", "why", "can", "the", "and",
        "for", "with", "that", "this", "from", "tell", "read", "about", "there", "ther",
        "whats", "hello", "hey", "good", "morning", "evening", "sweety", "please", "help"
    }
    keywords = [w.lower() for w in re.findall(r'\w+', query) if len(w) > 2 and w.lower() not in stop_words]
    if not keywords:
        return ""

    matches = []
    for folder in ["knowledge_base_docs", "precedents"]:
        fdir = os.path.join(BASE_DIR, folder)
        if os.path.exists(fdir):
            for fn in os.listdir(fdir):
                fp = os.path.join(fdir, fn)
                if os.path.isfile(fp) and fn.endswith((".txt", ".md", ".json")):
                    try:
                        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                            txt = f.read()
                        if sum(1 for k in keywords if k in txt.lower()) >= max(1, len(keywords) // 2):
                            matches.append(f"[{fn}]:\n{txt[:1500].strip()}")
                            if len(matches) >= 2:
                                break
                    except Exception:
                        pass
    return "\n\n".join(matches)


def sweety_execute(user_input: str) -> str:
    SweetySelfHealer.ensure_system()
    u_low = user_input.strip().lower()
    if not u_low:
        return ""

    # 1. Conversational / Greeting / Status Check -> Directly answered by SweetyBrain (NO ChromaDB dump)
    conversational_phrases = [
        "how are you", "how r u", "how are u", "hello", "hi ", "hey",
        "good morning", "good evening", "good afternoon", "who are you",
        "are you working", "are you online", "whats up", "what's up", "thank you", "thanks"
    ]
    if u_low in ["hi", "hello", "hey", "status"] or any(p in u_low for p in conversational_phrases):
        return (
            "======================================================================\n"
            "  SWEETYAI\n"
            "======================================================================\n"
            + SweetyBrain.respond(user_input) + "\n"
            "======================================================================"
        )

    # 2. System Health Check across all 36 modules
    if any(k in u_low for k in ["health", "verify all", "check all", "fix all", "repair all"]):
        print("[*] Sweety calling `health_check.py` and `verify_all_modules.py`...")
        h_out = sweety_call_module("health_check", user_input)
        v_out = sweety_call_module("verify_all_modules", user_input)
        return (
            "======================================================================\n"
            "  SWEETYAI — 36-MODULE & SYSTEM DIAGNOSTICS\n"
            "======================================================================\n"
            f"{h_out}\n{v_out}\n"
            "======================================================================"
        )

    # 3. PDF / Document Reading & Plain-English Legal Explanation
    if any(k in u_low for k in [
        "pdf", "download", "read", "ingest", "whats ther", "what's there",
        "what is in", "whats in", "tell me what", "7675c73a", "in that", "summarize", "explain"
    ]):
        print("[*] Sweety reading and analyzing document...")
        pdf_path, full_text = sweety_read_document(user_input)
        if pdf_path and full_text:
            analysis = SweetyBrain.summarize_legal_text(full_text, os.path.basename(pdf_path))
            return (
                "======================================================================\n"
                "  SWEETYAI — LEGAL DOCUMENT ANALYSIS\n"
                "======================================================================\n"
                + analysis + "\n"
                "======================================================================"
            )

    # 4. Specialized Legal Modules (All 36+ Modules)
    for keywords, mod_name, out_dir in SWEETY_ENGINES:
        if any(k in u_low for k in keywords):
            print(f"[*] Sweety calling module `{mod_name}.py`...")
            mod_out = sweety_call_module(mod_name, user_input, out_dir)
            if mod_name == "advocate_diary" and os.path.exists(os.path.join(BASE_DIR, "free_notifier.py")):
                notif_out = sweety_call_module("free_notifier", user_input)
                mod_out = f"{mod_out}\n{notif_out}".strip()
            return (
                "======================================================================\n"
                f"  SWEETYAI — MODULE EXECUTION (`{mod_name}.py`)\n"
                "======================================================================\n"
                f"{mod_out if mod_out else f'[✓] `{mod_name}.py` completed.'}\n"
                "======================================================================"
            )

    # 5. General Legal Question -> Filtered RAG + SweetyBrain Response
    rag_ctx = search_relevant_rag_only(user_input)
    reply = SweetyBrain.respond(user_input, rag_ctx)
    return (
        "======================================================================\n"
        "  SWEETYAI\n"
        "======================================================================\n"
        + reply + "\n"
        "======================================================================"
    )


def sweety_interactive_chat():
    print("======================================================================")
    print("  SWEETYAI — OFFLINE LEGAL WORKSTATION")
    print("  Type any question or command. Type 'exit' to quit.")
    print("======================================================================")
    while True:
        try:
            msg = input("\nSweety ❯ ").strip()
            if not msg:
                continue
            if msg.lower() in ["exit", "quit", "q"]:
                print("[✓] Closing interactive session.")
                break
            print(sweety_execute(msg))
        except (KeyboardInterrupt, EOFError):
            print("\n[✓] Closing interactive session.")
            break
        except Exception as e:
            print(f"[*] Sweety handled error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd_str = " ".join(sys.argv[1:]).strip()
        if cmd_str.lower() in ["chat", "console", "interactive"]:
            sweety_interactive_chat()
        else:
            print(sweety_execute(cmd_str))
    else:
        sweety_interactive_chat()
