# SweetyAI API bridge

The Tauri frontend expects your existing Python agent to expose one local endpoint:

POST http://127.0.0.1:8765/chat

Request:
{"message":"Hello"}

Response:
{"ok":true,"content":"Hello!"}

Keep the model/API key inside the Python process. Do not put the API key in the browser frontend.

## Minimal standard-library bridge

Create `app/server.py` in your existing SweetyAI project and adapt the two marked lines to your existing model-loading code.
