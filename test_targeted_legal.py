import requests
import json

url = "http://127.0.0.1:8765/rag-chat"
payload = {
    "message": "Analyze the precise distinction and statutory requirements between culpable homicide amounting to murder under Section 300 IPC and culpable homicide not amounting to murder, citing relevant local notes or principles."
}
headers = {"Content-Type": "application/json"}

try:
    print("Sending targeted legal query to Sweety RAG backend...")
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Status Code: {response.status_code}")
    print("Response:\n", json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error executing targeted legal query: {e}")
