import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading

from app.main import load_model
from app.agent.agent import Agent

HOST = "127.0.0.1"
PORT = 8765

print("Loading SweetyAI model for API bridge...")
tokenizer, model = load_model()
agent = Agent(model=model, tokenizer=tokenizer)
agent_lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send_json(204, {})

    def do_POST(self):
        if self.path != "/chat":
            self._send_json(404, {"ok": False, "error": "Not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            payload = json.loads(raw.decode("utf-8"))
            message = str(payload.get("message", "")).strip()

            if not message:
                self._send_json(400, {"ok": False, "error": "Message is empty"})
                return

            # Agent.chat keeps conversational state, so serialize requests.
            with agent_lock:
                answer = agent.chat(message)

            self._send_json(200, {"ok": True, "content": answer})

        except Exception as exc:
            self._send_json(500, {"ok": False, "error": str(exc)})

    def log_message(self, fmt, *args):
        print(f"[SweetyAI API] {self.address_string()} - {fmt % args}")


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"SweetyAI API listening on http://{HOST}:{PORT}")
    server.serve_forever()
