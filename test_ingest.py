import requests
import json

# 1. Ingest new legal text
ingest_url = "http://127.0.0.1:8765/ingest"
ingest_payload = {
    "title": "Landmark Supreme Court Precedent on Bail",
    "content": "The fundamental principle of criminal jurisprudence is that bail is the rule and jail is the exception, as reaffirmed in landmark judgments regarding personal liberty under Article 21 of the Constitution.",
    "source": "Supreme Court Precedents Digest"
}
headers = {"Content-Type": "application/json"}

print("Sending document to ingestion endpoint...")
ingest_response = requests.post(ingest_url, data=json.dumps(ingest_payload), headers=headers)
print(f"Ingest Status Code: {ingest_response.status_code}")
print("Ingest Response:", json.dumps(ingest_response.json(), indent=2))

# 2. Query the RAG endpoint immediately to verify retrieval
rag_url = "http://127.0.0.1:8765/rag-chat"
rag_payload = {
    "message": "What is the rule regarding bail according to Supreme Court precedents?"
}

print("\nVerifying ingestion via RAG query...")
rag_response = requests.post(rag_url, data=json.dumps(rag_payload), headers=headers)
print(f"RAG Status Code: {rag_response.status_code}")
print("RAG Response:\n", json.dumps(rag_response.json(), indent=2))
