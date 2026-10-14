import os
import requests

BASE_URL = "http://127.0.0.1:8765"


def batch_ingest(folder_path):
    if not os.path.exists(folder_path):
        print(f"[Error] Directory '{folder_path}' does not exist.")
        return

    files = [f for f in os.listdir(folder_path) if not f.startswith(".")]
    print(f"\n=== SweetyAI Bulk E-Discovery & Transcript Ingestion ===")
    print(f"Target Directory : {folder_path}")
    print(f"Files Discovered : {len(files)} file(s)\n")

    success_count = 0
    for fname in sorted(files):
        fpath = os.path.join(folder_path, fname)
        if not os.path.isfile(fpath):
            continue

        text_content = ""
        if fname.endswith((".txt", ".md", ".csv", ".json")):
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                text_content = f.read()
        elif fname.endswith(".pdf"):
            try:
                import pymupdf
                doc = pymupdf.open(fpath)
                text_content = "\n".join(page.get_text("text") for page in doc)
            except Exception as e:
                print(f"  [!] PDF warning on {fname}: {e}")
                continue

        if text_content.strip():
            doc_id = f"discovery-{fname.replace('.', '-')}"
            try:
                resp = requests.post(
                    f"{BASE_URL}/ingest",
                    json={
                        "doc_id": doc_id,
                        "text": text_content,
                        "source": f"Bulk E-Discovery Sync ({fname})",
                    },
                    timeout=10,
                )
                if resp.status_code == 200:
                    print(f"  [OK] Ingested '{fname}' ({len(text_content)} chars) -> ID: {doc_id}")
                    success_count += 1
                else:
                    print(f"  [X] Failed '{fname}': status {resp.status_code}")
            except Exception as e:
                print(f"  [X] Connection error on '{fname}': {e}")

    print("---------------------------------------------------------")
    print(f"[Success] Bulk ingestion complete! {success_count}/{len(files)} files indexed into ChromaDB.")
    print("=========================================================\n")
