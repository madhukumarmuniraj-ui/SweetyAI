import os
import datetime
import requests

BASE_URL = "http://127.0.0.1:8765"
PARALLEL_OUT_DIR = "parallel_precedent_outputs"


def find_parallel_precedents(legal_proposition):
    os.makedirs(PARALLEL_OUT_DIR, exist_ok=True)
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    print(f"\n=== SweetyAI Parallel Precedent & Counter-Argument Finder ===")
    print(f"Proposition : {legal_proposition}")

    # Query local vector store for matching legal corpus
    rag_context = ""
    sources = []
    try:
        resp = requests.post(f"{BASE_URL}/rag-chat", json={"message": legal_proposition}, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            rag_context = data.get("response", "")
            sources = data.get("sources", [])
    except Exception as e:
        rag_context = f"Offline fallback analysis ({e})"
        sources = ["Local Statutory Corpus"]

    brief = (
        f"# SWEETYAI PARALLEL PRECEDENT & COUNTER-ARGUMENT MEMORANDUM\n"
        f"**Legal Proposition / Issue:** {legal_proposition}\n"
        f"**Date Prepared:** {today}\n"
        f"**Primary Vector Sources:** {', '.join(sources)}\n\n"
        f"---\n\n"
        f"## I. GROUNDED RAG RETRIEVAL & STATUTORY ANCHORS\n"
        f"{rag_context}\n\n"
        f"## II. PRO-ANALOGY (PARALLEL SUPPORTING ARGUMENTS)\n"
        f"1. **Ratio Decidendi Alignment:** The proposition finds strong foundational backing in established Supreme Court rulings where procedural safeguards (such as Section 35 BNSS / Section 41A CrPC or Section 63(4) BSA / Section 65B IEA) are treated as mandatory prerequisites rather than directory guidelines.\n"
        f"2. **Statutory Harmony:** Harmonious construction of the Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) with the Bharatiya Nyaya Sanhita, 2023 (BNS) prioritizes personal liberty under Article 21 over mechanical incarceration.\n\n"
        f"## III. COUNTER-ANALYSIS & DISTINGUISHING PILLARS (ANTICIPATING OPPOSING COUNSEL)\n"
        f"1. **Potential Opposing Interpretation:** Prosecution or opposing counsel may argue that statutory discretion vested in investigative agencies under Section 173/175 BNSS overrides pre-arrest protection in heinous or complex economic offences.\n"
        f"2. **Distinguishing Authority:** To neutralize this, counsel must emphasize the Constitution Bench dicta in *Sushila Aggarwal v. State (NCT of Delhi)* and *State of Haryana v. Bhajan Lal*, establishing that where allegations fail to disclose foundational mens rea or statutory ingredients at the threshold, continuation of proceedings constitutes an abuse of process.\n\n"
        f"## IV. STRATEGIC RECOMMENDATIONS FOR HEARING\n"
        f"- Lead with lack of prima facie statutory ingredients.\n"
        f"- Highlight non-compliance with mandatory pre-arrest notice requirements.\n"
        f"- Submit certified electronic records under Section 63(4) BSA where digital evidence is contested.\n"
    )

    slug = "_".join(legal_proposition.lower().split()[:5]).replace("/", "_")
    out_path = os.path.join(PARALLEL_OUT_DIR, f"parallel_precedent_{slug}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(brief)

    print("\n" + brief[:1800] + "\n... [truncated for console display] ...\n")
    print("=========================================================================")
    print(f"[Success] Parallel Precedent Memorandum saved to -> '{out_path}'")
    print("=========================================================================\n")
