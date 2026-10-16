import os
import sys
import gc
import warnings
import threading
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Memory optimization settings
os.environ.update({
    "TORCH_CPP_LOG_LEVEL": "ERROR",
    "TOKENIZERS_PARALLELISM": "false",
    "OMP_NUM_THREADS": "4",
    "MKL_NUM_THREADS": "4"
})

warnings.filterwarnings("ignore")
gc.set_threshold(100, 5, 5)

HOST = "0.0.0.0"
PORT = 8765

# Model paths (all local to this repo)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIGHTWEIGHT_MODEL = None  # quick replies are built in, no model needed
DEEP_MODEL_PATH = os.path.join(
    BASE_DIR, "SweetyAI-Core", "Qwen2.5-Coder-3B-Instruct-abliterated-Q4_K_M.gguf"
)  # Qwen 3B GGUF for coding & analysis (requires llama-cpp-python)

# Deep thinking triggers - when to use powerful model
DEEP_THINKING_TRIGGERS = [
    'analyze', 'research', 'legal', 'contract', 'law', 'statute', 'case',
    'deep', 'complex', 'detailed', 'comprehensive', 'investigate', 'examine',
    'review', 'study', 'evaluate', 'assess', 'explain in detail', 'thorough',
    'legal analysis', 'case law', 'precedent', 'regulatory', 'compliance',
    'due diligence', 'risk assessment', 'strategic', 'policy', 'framework'
]

class HybridAgent:
    def __init__(self):
        self.lightweight_responses = [
            "I'm here to help! For quick questions, I'll respond instantly. For deep analysis or legal research, I'll switch to my more powerful reasoning mode.",
            "What can I assist you with today? I can handle quick queries immediately or engage deep analysis mode for complex tasks.",
            "Ready to help! I'll use quick responses for simple queries and activate advanced reasoning for complex analysis.",
            "How can I help? I have both quick response mode and deep thinking capabilities for research and analysis."
        ]
        self.counter = 0
        self.deep_model = None
        self.deep_model_loaded = False

    def needs_deep_thinking(self, message):
        """Determine if message requires deep analysis model"""
        message_lower = message.lower()

        # Check for explicit deep thinking requests
        if any(trigger in message_lower for trigger in DEEP_THINKING_TRIGGERS):
            return True

        # Check for complex questions (long queries, multiple parts)
        if len(message) > 200 or message.count('?') > 1:
            return True

        # Check for code analysis requests
        if any(word in message_lower for word in ['debug', 'optimize', 'refactor', 'algorithm', 'architecture']):
            return True

        return False

    def load_deep_model(self):
        """Load the powerful model for deep analysis"""
        if self.deep_model_loaded:
            return True

        try:
            if not os.path.exists(DEEP_MODEL_PATH):
                print(f"[SweetyAI] Deep model not found at {DEEP_MODEL_PATH}")
                return False

            print("[SweetyAI] Loading deep analysis model (Qwen2.5-Coder-3B GGUF)...")

            # GGUF models run through llama-cpp-python (tokenizer is inside the GGUF)
            try:
                from llama_cpp import Llama
            except ImportError:
                print("[SweetyAI] llama-cpp-python not available, using fallback")
                return False

            self.deep_model = Llama(
                model_path=DEEP_MODEL_PATH,
                n_ctx=4096,
                n_threads=4,
                verbose=False
            )
            self.deep_model_loaded = True
            print("[SweetyAI] Deep analysis model loaded successfully!")
            return True

        except Exception as e:
            print(f"[SweetyAI] Could not load deep model: {e}")
            return False

    def unload_deep_model(self):
        """Unload deep model to free memory"""
        if self.deep_model:
            del self.deep_model
            self.deep_model = None
            self.deep_model_loaded = False
            gc.collect()
            print("[SweetyAI] Deep model unloaded, memory freed")

    def process_message(self, message):
        """Route message to appropriate model"""

        # Quick response for simple queries
        if not self.needs_deep_thinking(message):
            self.counter = (self.counter + 1) % len(self.lightweight_responses)
            response = self.lightweight_responses[self.counter]

            # Add context-aware quick responses
            if 'hello' in message.lower() or 'hi' in message.lower():
                return "Hello! I'm SweetyAI. I can provide quick responses or engage deep analysis mode for complex legal research and detailed analysis. What do you need help with?"
            elif 'how are you' in message.lower():
                return "I'm running optimally! Quick responses ready, and I can activate deep analysis mode when you need detailed research or legal analysis."
            elif 'what can you do' in message.lower():
                return "I can:\n• Provide quick responses for simple queries\n• Activate deep analysis mode for legal research\n• Code analysis and debugging\n• Document review and contract analysis\n• Complex reasoning and research tasks\n\nJust ask, and I'll use the appropriate mode!"

            return response

        # Deep analysis mode
        print("[SweetyAI] Activating deep analysis mode...")

        if not self.load_deep_model():
            return "I'd like to provide deep analysis for your query, but the advanced model isn't available. I can still help with basic responses. Please ensure llama-cpp-python is installed for full capabilities."

        try:
            # Use the powerful model for complex queries
            prompt = f"You are SweetyAI, an advanced AI assistant specializing in legal research, code analysis, and deep reasoning. Please provide a comprehensive response to: {message}"

            response = self.deep_model(
                prompt,
                max_tokens=1000,
                temperature=0.7,
                top_p=0.9,
                stop=["Human:", "User:"]
            )

            result = response['choices'][0]['text'].strip()

            # Unload model after use to save memory
            self.unload_deep_model()

            return f"🧠 **Deep Analysis Mode**\n\n{result}\n\n*Switched back to quick response mode to save memory.*"

        except Exception as e:
            self.unload_deep_model()
            return f"Deep analysis mode encountered an error: {e}. Falling back to quick response mode."

# Initialize hybrid agent
agent = HybridAgent()

class HybridSweetyHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "ok": True,
                "status": "online",
                "name": "SweetyAI Hybrid",
                "version": "0.3.0-hybrid",
                "modes": {
                    "quick_response": "built-in instant replies",
                    "deep_analysis": "Qwen2.5-Coder-3B GGUF (local, on-demand)",
                    "current_memory": "optimized"
                }
            }
            self.wfile.write(json.dumps(response).encode())
            return

        # Serve the hybrid interface
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            # Load the existing Claude Code-style interface
            try:
                with open("index.html", "r", encoding="utf-8") as f:
                    html = f.read()
                self.wfile.write(html.encode())
            except:
                # Fallback minimal interface
                html = """<!DOCTYPE html>
<html>
<head><title>SweetyAI Hybrid</title></head>
<body style="font-family: Arial; background: #1a1a1a; color: #fff; padding: 20px;">
    <h1>🔥 SweetyAI - Hybrid Intelligence</h1>
    <p><strong>Quick Mode:</strong> Instant responses using lightweight model</p>
    <p><strong>Deep Mode:</strong> Activates automatically for complex analysis</p>
    <div id="chat" style="height: 400px; overflow-y: auto; border: 1px solid #333; padding: 10px; margin: 10px 0; background: #2a2a2a;"></div>
    <input type="text" id="input" style="width: 70%; padding: 10px; background: #333; border: 1px solid #555; color: #fff;" placeholder="Ask anything...">
    <button onclick="send()" style="padding: 10px 20px; background: #0066cc; color: #fff; border: none;">Send</button>
    <script>
        function send() {
            const input = document.getElementById('input');
            const message = input.value.trim();
            if (!message) return;

            document.getElementById('chat').innerHTML += '<div><strong>You:</strong> ' + message + '</div>';
            input.value = '';

            fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: message})
            }).then(r => r.json()).then(data => {
                document.getElementById('chat').innerHTML += '<div><strong>SweetyAI:</strong> ' + data.response + '</div>';
                document.getElementById('chat').scrollTop = document.getElementById('chat').scrollHeight;
            });
        }
        document.getElementById('input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') send();
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

                # Process with hybrid agent
                response = agent.process_message(message)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()

                result = {"response": response, "status": "success"}
                self.wfile.write(json.dumps(result).encode())

                # Aggressive garbage collection
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
    print(f"[SweetyAI] Starting hybrid intelligence server on {HOST}:{PORT}")
    print(f"[SweetyAI] Quick Mode: built-in instant replies")
    print(f"[SweetyAI] Deep Mode: Qwen2.5-Coder-3B GGUF (loads on-demand)")
    print(f"[SweetyAI] Memory: Optimized hybrid system")

    server = ThreadingHTTPServer((HOST, PORT), HybridSweetyHandler)
    server.daemon_threads = True

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[SweetyAI] Shutting down hybrid server...")
        if agent.deep_model_loaded:
            agent.unload_deep_model()
        server.shutdown()
        gc.collect()