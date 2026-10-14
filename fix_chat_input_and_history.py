import os

paths = ["/home/madhukumarm/SweetyAI/index.html", "/home/madhukumarm/SweetyAI/dist/index.html"]

for path in paths:
    if not os.path.exists(path):
        continue
        
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # We will inject a robust input controller script right before </body>
    controller_code = """
    <script>
    // SweetyAI Robust Input Controller (Enter to send, Up-arrow for history)
    (function() {
        let messageHistory = [];
        let historyIndex = -1;

        document.addEventListener('DOMContentLoaded', () => {
            // Find input dynamically (supports textarea or input with id chat-input, textarea, etc.)
            const inputEl = document.getElementById('chat-input') || document.getElementById('textarea') || document.querySelector('textarea') || document.querySelector('input[type="text"]');
            const sendBtn = document.getElementById('send-btn') || document.getElementById('sendBtn');

            if (!inputEl) return;

            inputEl.addEventListener('keydown', function(e) {
                // Up Arrow: History recall
                if (e.key === 'ArrowUp') {
                    if (messageHistory.length > 0) {
                        e.preventDefault();
                        if (historyIndex < messageHistory.length - 1) {
                            historyIndex++;
                        }
                        inputEl.value = messageHistory[messageHistory.length - 1 - historyIndex];
                    }
                    return;
                }

                // Down Arrow: Next history item
                if (e.key === 'ArrowDown') {
                    if (historyIndex > 0) {
                        e.preventDefault();
                        historyIndex--;
                        inputEl.value = messageHistory[messageHistory.length - 1 - historyIndex];
                    } else if (historyIndex === 0) {
                        e.preventDefault();
                        historyIndex = -1;
                        inputEl.value = '';
                    }
                    return;
                }

                // Enter Key: Send message
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    const text = inputEl.value.trim();
                    if (!text) return;

                    // Save to history
                    messageHistory.push(text);
                    historyIndex = -1;

                    // Trigger the send function
                    if (typeof handleSendMessage === 'function') {
                        // Ensure textarea.value is populated so handleSendMessage grabs it
                        inputEl.value = text;
                        handleSendMessage(e);
                    } else if (typeof sendMessage === 'function') {
                        sendMessage();
                    } else if (sendBtn) {
                        sendBtn.click();
                    }
                }
            });
        });
    })();
    </script>
    </body>
    """

    if "SweetyAI Robust Input Controller" not in content:
        content = content.replace("</body>", controller_code)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Patched input controller into: {path}")
    else:
        print(f"Input controller already present in: {path}")

