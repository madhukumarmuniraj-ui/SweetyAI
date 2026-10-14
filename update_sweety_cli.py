with open("sweety.py", "r") as f:
    code = f.read()

# We will add a legal subcommand parser to sweety.py
old_main_start = """def main():
    parser = argparse.ArgumentParser(
        prog="sweety",
        description="SweetyAI local agent (same engine as the desktop UI).",
    )
    parser.add_argument(
        "prompt",
        nargs="*",
        help="One-shot request. Omit for interactive chat.",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Auto-approve tool actions (run_command, edit_file, ...) instead of asking.",
    )
    args = parser.parse_args()"""

new_main_start = """import requests
import json

BASE_URL = "http://127.0.0.1:8765"

def query_rag(message):
    try:
        response = requests.post(f"{BASE_URL}/rag-chat", json={"message": message})
        if response.status_code == 200:
            data = response.json()
            print("\\n=== Sweety Legal AI Analysis ===")
            print(f"Response:\\n{data.get('response')}")
            if data.get('sources'):
                print(f"\\nSources Cited: {', '.join(data.get('sources'))}")
            print("================================\\n")
        else:
            print(f"Error: Server returned status {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Connection error to legal server (is server.py running?): {e}")

def ingest_doc(doc_id, text, source):
    try:
        response = requests.post(f"{BASE_URL}/ingest", json={
            "doc_id": doc_id,
            "text": text,
            "source": source
        })
        if response.status_code == 200:
            print("\\n[Success] Document successfully ingested into legal vector DB.")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error during ingestion: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")

def main():
    parser = argparse.ArgumentParser(
        prog="sweety",
        description="SweetyAI local agent & legal assistant.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # Legal subcommand group
    legal_parser = subparsers.add_parser("legal", help="Sweety Legal AI RAG commands")
    legal_subparsers = legal_parser.add_subparsers(dest="legal_command", required=True)

    # legal query
    q_parser = legal_subparsers.add_parser("query", help="Query the legal RAG database")
    q_parser.add_argument("text", type=str, help="The legal question or prompt")

    # legal ingest
    i_parser = legal_subparsers.add_parser("ingest", help="Ingest legal document into vector store")
    i_parser.add_argument("--doc-id", required=True, help="Unique document ID")
    i_parser.add_argument("--text", required=True, help="Body text/content")
    i_parser.add_argument("--source", required=True, help="Source citation")

    # General agent arguments
    parser.add_argument(
        "prompt",
        nargs="*",
        help="One-shot request. Omit for interactive chat.",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Auto-approve tool actions.",
    )
    args = parser.parse_args()

    if args.command == "legal":
        if args.legal_command == "query":
            query_rag(args.text)
            return
        elif args.legal_command == "ingest":
            ingest_doc(args.doc_id, args.text, args.source)
            return"""

if old_main_start in code:
    code = code.replace(old_main_start, new_main_start)
    with open("sweety.py", "w") as f:
        f.write(code)
    print("Successfully patched sweety.py with 'sweety legal' commands!")
else:
    print("Could not find exact match block. Let's check alternative structure.")
