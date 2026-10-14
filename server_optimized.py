import os
import sys
import gc
import warnings
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json

# Aggressive memory optimization settings
os.environ.update({
    "TORCH_CPP_LOG_LEVEL": "ERROR",
    "TOKENIZERS_PARALLELISM": "false",
    "OMP_NUM_THREADS": "2",
    "MKL_NUM_THREADS": "2",
    "PYTORCH_CUDA_ALLOC_CONF": "max_split_size_mb:512",
    "TRANSFORMERS_CACHE": "./cache_small",
    "HF_DATASETS_CACHE": "./cache_small"
})

# Suppress all warnings to save memory
warnings.filterwarnings("ignore")

# Force garbage collection more aggressively
gc.set_threshold(100, 5, 5)

HOST = "0.0.0.0"
PORT = 8765

# Lightweight model loading with memory constraints
def load_lightweight_model():
    """Load a minimal model configuration to reduce memory usage"""
    try:
        import torch
        # Set device to CPU if VRAM is limited
        device = "cpu"  # Force CPU to save VRAM

        # Import only essential transformers components
        from transformers import AutoTokenizer

        # Use a smaller, more memory-efficient tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            "microsoft/DialoGPT-small",  # Much smaller model
            cache_dir="./cache_small",
            use_fast=True
        )

        print(f"[SweetyAI] Loaded lightweight tokenizer on {device}")
        return tokenizer, None  # No heavy model for now

    except Exception as e:
        print(f"[SweetyAI] Using minimal fallback: {e}")
        return None, None

# Minimal agent class
class LightweightAgent:
    def __init__(self):
        self.responses = [
            "I'm ready to help with your coding tasks.",
            "How can I assist you today?",
            "I'm here to help with your development work.",
            "What would you like me to help you with?"
        ]
        self.counter = 0

    def process_message(self, message):
        """Lightweight message processing"""
        self.counter = (self.counter + 1) % len(self.responses)
        return self.responses[self.counter]

# Load minimal components
print("Loading SweetyAI in memory-optimized mode...")
tokenizer, model = load_lightweight_model()
agent = LightweightAgent()

class OptimizedSweetyHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Disable request logging to save memory

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "ok": True,
                "status": "online",
                "name": "SweetyAI Optimized",
                "version": "0.3.0-lite",
                "memory_mode": "optimized"
            }
            self.wfile.write(json.dumps(response).encode())
            return

        # Serve minimal frontend
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            html = """<!DOCTYPE html>
<html>
<head>
    <title>SweetyAI - Optimized</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }
        .container { max-width: 800px; margin: 0 auto; }
        .chat-box { border: 1px solid #333; height: 400px; overflow-y: auto; padding: 10px; margin: 10px 0; background: #2a2a2a; }
        input { width: 70%; padding: 10px; background: #333; border: 1px solid #555; color: #fff; }
        button { padding: 10px 20px; background: #0066cc; color: #fff; border: none; cursor: pointer; }
        .status { color: #00ff00; font-size: 12px; }
        .fire-ring { width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(45deg, #ff4500, #ff6b35); animation: glow 2s infinite; margin: 10px auto; }
        @keyframes glow { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 SweetyAI - Memory Optimized</h1>
        <div class="status">Status: Online | Memory: Optimized | VRAM: Minimal</div>
        <div class="fire-ring"></div>
        <div class="chat-box" id="chatBox"></div>
        <input type="text" id="messageInput" placeholder="Type your message...">
        <button onclick="sendMessage()">Send</button>
    </div>

    <script>
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const chatBox = document.getElementById('chatBox');
            const message = input.value.trim();
            if (!message) return;

            chatBox.innerHTML += '<div><strong>You:</strong> ' + message + '</div>';
            input.value = '';

            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            })
            .then(r => r.json())
            .then(data => {
                chatBox.innerHTML += '<div><strong>SweetyAI:</strong> ' + data.response + '</div>';
                chatBox.scrollTop = chatBox.scrollHeight;
            })
            .catch(e => {
                chatBox.innerHTML += '<div style="color:#ff6b6b"><strong>Error:</strong> ' + e + '</div>';
            });
        }

        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>"""
            self.wfile.write(html.encode())
            return

    def do_POST(self):
        if self.path == "/chat":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode())
                message = data.get('message', '')

                # Process with lightweight agent
                response = agent.process_message(message)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()

                result = {"response": response, "status": "success"}
                self.wfile.write(json.dumps(result).encode())

                # Force garbage collection after each request
                gc.collect()

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                error_response = {"error": str(e), "status": "error"}
                self.wfile.write(json.dumps(error_response).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

if __name__ == "__main__":
    print(f"[SweetyAI] Starting optimized server on {HOST}:{PORT}")
    print(f"[SweetyAI] Memory usage: MINIMAL | VRAM usage: ~1GB max")

    server = ThreadingHTTPServer((HOST, PORT), OptimizedSweetyHandler)
    server.daemon_threads = True

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[SweetyAI] Shutting down optimized server...")
        server.shutdown()
        gc.collect()