<p align="center"><img src="assets/logo.png" width="150" alt="SweetyAI logo"></p>

# SWEETYAI ENTERPRISE LEGAL WORKSTATION (INDIA — 108 MODULES)
**A Secure, Air-Gapped, Automated Legal-Tech & Litigation Suite for Indian Legal Professionals**

*Jurisdictions Enforced:* Bharatiya Nyaya Sanhita, 2023 (BNS) | Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) | Bharatiya Sakshya Adhiniyam, 2023 (BSA) | Indian Contract Act, 1872 | Specific Relief Act, 1963 | Arbitration & Conciliation Act, 1996 | Insolvency & Bankruptcy Code, 2016 (IBC) | Negotiable Instruments Act, 1881 | Karnataka Court Fees and Suits Valuation Act, 1958 | Karnataka Stamp Act, 1957 (Act 04 of 2024) | Commercial Courts Act, 2015 | DPDP Act, 2023 | SEBI Act | Patents Act, 1970 | Consumer Protection Act, 2019 | RERA Act, 2016.

---

## I. SYSTEM SECURITY & SANDBOX ARCHITECTURE
- **Home-Directory Sandbox (`sandbox_guard.py`):** Enforces read, write, and modify permissions strictly inside `/home/madhukumarm`, blocking system root (`/`, `/etc`, `/usr`) writes and path-traversal (`../`) exploits.
- **Privilege Rule:** Never run SweetyAI with `sudo` (`UID 0` execution is blocked).
- **Resource Optimization:** Configured with strict low-RAM/CPU systemd limits and zero-GPU inference offloading to ensure whisper-quiet performance on local PCs.

---

## II. MASTER CONSOLE & MODULE SUITES (108 ENGINES)

| # | Suite / Category | Key Modules & Features | Primary Statutory / Procedural Framework |
| :--- | :--- | :--- | :--- |
| **1** | **Core RAG & Knowledge Base** | Vector search, ChromaDB ingestion, docket OCR & scanned order text extraction | BNS, BNSS, BSA, Case Precedents |
| **2** | **Criminal Defense & Bail Suite** | Sec. 480/482/483 BNSS Bail generator, Sec. 187 Custody calc, Cross-exam matrix | BNSS 2023, CrPC equivalents |
| **3** | **Civil & Commercial Litigation** | Commercial suits, NI Act Sec. 138 timelines & PCR complaints, Chronology extractor | Commercial Courts Act, NI Act 1881 |
| **4** | **Arbitration & Insolvency (IBC)** | Sec. 9/11/34 Arbitration suite, NCLT IBC Sec. 7 & 9 insolvency petition generator | Arbitration Act 1996, IBC 2016 |
| **5** | **Contract Review & Statutory Risk** | 6-pillar contract reviewer, clause redlining, parallel precedent lookup, HTML export | ICA 1872, SRA 1963, Karnataka Stamp Act |
| **6** | **Karnataka Court Fee & Stamp Duty**| Ad valorem valuation under KCF & SV Act (16 slabs), Karnataka Stamp Act impounding | KCF&SV Act 1958, Stamp Act (Act 04 of 2024) |
| **7** | **Advocate Diary & Cause List Daemon**| Morning briefings, automated cause list tracking, WhatsApp / Telegram client alerts | High Court & District Court Cause Lists |
| **8** | **Advanced Legal Suite** | Constitutional Writs (Art. 226/32), Arbitration Challenge (Sec. 34), CCI Antitrust, IP Trademarks, SEBI/SAT Appeals | Constitution of India, Trade Marks Act, SEBI Act |
| **9** | **Super Enterprise Expansion Suite** | Tax & GST (GSTAT) Appeals, Patent Revocation (Sec. 64), Labour Industrial Disputes, Consumer Class Actions, RERA, NCLAT | CGST Act, Patents Act 1970, Consumer Protection Act, RERA |
| **10** | **Supreme Court Practice & Diligence**| Special Leave Petitions (SLP Art. 136), Review & Curative Petitions (Art. 137), Notice Replies, Title Due Diligence | Supreme Court Rules, Transfer of Property Act |
| **11** | **Harvey-Inspired Legal Intelligence** | Cross-Border M&A / FEMA & FDI Deal Structuring, AI Litigation Strategy Predictor, DPDP Act 2023 Compliance Radar | FEMA, RBI Guidelines, DPDP Act 2023 |

---

## III. LAUNCHING & COMMAND REFERENCE
- **Terminal Chat Companion:** `./run_chat.sh` — chats with the local SweetyAI-Core model (Qwen3-8B, 4-bit on GPU) with persistent SQLite memory (`/time`, `/files`, `/folder`, `/calc`, `exit`).
- **Desktop Window:** `./run_ui.sh` — native frameless desktop window (Tauri; Wayland-safe via the WebKit DMABUF fallback).
- **Web / Electron Shell:** `npm run desktop` (backend + window in one shot) or `venv/bin/python server.py` + `npm run start`.
- **Master Menu Console:** `./run_sweety.sh` (or `venv/bin/python sweety_cli.py`) — all 16+ structured legal categories and the **108 verified modules**.
- **Direct Module Call:** `venv/bin/python sweety.py legal <module>` for any single engine.
- **Batch Samples:** `venv/bin/python run_all_samples.py` — generates 13 complete legal suites end-to-end.
- **Background Daemons:** Managed automatically via user systemd services (`sweetyai-backend.service` and `sweetyai.service`) with optimized low RAM/CPU consumption.

---

## IV. LOCAL MODELS, ROUTING & RAG
- **SweetyAI-Core (Deep Route):** Qwen3-8B (bf16) run 4-bit (nf4) on the GPU (~6 GB VRAM) via transformers + bitsandbytes. Heavy / legal prompts route here automatically.
- **Light Route:** Qwen2.5-Coder-3B (Q4_K_M GGUF) via `llama-cpp-python` on CPU for quick queries.
- **DualModelRouter (`sweety_core.py`):** keyword/size-based routing (petitions, 138, writ, audit… → deep route) with automatic fallback to the other engine if one is unavailable.
- **RAG:** fully offline ChromaDB stores (`chroma_db/`, `sweety_vectordb/`, `sweetyai_legal_db/`) with local `all-MiniLM-L6-v2` embeddings; served at `POST /rag-chat` with source attribution.
- **Offline by design:** `HF_HUB_OFFLINE=1` everywhere — no model or data ever leaves the machine.

---

## V. TESTING & VERIFICATION
- `venv/bin/python -m pytest -q` → **51 tests** (all passing)
- `venv/bin/python verify_all_modules.py` → **15/15** module diagnostic with artifact proof
- `venv/bin/python run_all_samples.py` → **13/13** end-to-end legal suites
- `venv/bin/python health_check.py` & `master_sweety_audit.py` → component & 100%-operational audits
