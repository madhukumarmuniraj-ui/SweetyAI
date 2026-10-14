import requests
import json

url = "http://127.0.0.1:8765/rag-chat"
payload = {
    "message": "Summarize the key legal principles, statutes, or precedents indexed in the legal database."
}
headers = {"Content-Type": "application/json"}

try:
    print("Sending query to legal RAG pipeline...")
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Status Code: {response.status_code}")
    print("Response:\n", json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error connecting to RAG endpoint: {e}")
