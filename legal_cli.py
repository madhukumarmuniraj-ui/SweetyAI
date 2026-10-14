import sys
import argparse
import requests
import json

BASE_URL = "http://127.0.0.1:8765"

def query_rag(message):
    try:
        response = requests.post(f"{BASE_URL}/rag-chat", json={"message": message})
        if response.status_code == 200:
            data = response.json()
            print("\n=== Sweety Legal AI Analysis ===")
            print(f"Response:\n{data.get('response')}")
            if data.get('sources'):
                print(f"\nSources Cited: {', '.join(data.get('sources'))}")
            print("================================\n")
        else:
            print(f"Error: Server returned status {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Connection error: {e}")

def ingest_doc(doc_id, text, source):
    try:
        response = requests.post(f"{BASE_URL}/ingest", json={
            "doc_id": doc_id,
            "text": text,
            "source": source
        })
        if response.status_code == 200:
            print("\n[Success] Document successfully ingested into legal vector DB.")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error during ingestion: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sweety AI Legal Research Assistant CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Query command
    q_parser = subparsers.add_parser("query", help="Run a RAG query against your legal database")
    q_parser.add_argument("text", type=str, help="The legal question or prompt")

    # Ingest command
    i_parser = subparsers.add_parser("ingest", help="Ingest a new legal document or note")
    i_parser.add_argument("--doc-id", required=True, help="Unique identifier or ID for the document")
    i_parser.add_argument("--text", required=True, help="Main body text/content")
    i_parser.add_argument("--source", required=True, help="Source citation or reference")

    args = parser.parse_args()

    if args.command == "query":
        query_rag(args.text)
    elif args.command == "ingest":
        ingest_doc(args.doc_id, args.text, args.source)
