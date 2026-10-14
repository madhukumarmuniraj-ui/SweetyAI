import os

paths = ["/home/madhukumarm/SweetyAI/index.html", "/home/madhukumarm/SweetyAI/dist/index.html"]

for path in paths:
    if not os.path.exists(path):
        continue
        
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove all our previous injected blocks to start fresh
    if "globalMessageHistory" in content:
        # Simple cleanup of the injected script block
        parts = content.split("<script>\n    let globalMessageHistory")
        content = parts[0] + "</body>" if len(parts) > 1 else content

    # Inject a robust, clean controller that properly binds to #textarea and handleSendMessage
    fix_script = """
    <script>
    let chatHistory = [];
    let historyIdx = -1;

    // Ensure handleSendMessage correctly grabs the textarea value and clears it
    window.addEventListener('DOMContentLoaded', () => {
        const ta = document.getElementById('textarea');
        if (!ta) return;

        ta.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowUp') {
                if (chatHistory.length > 0) {
                    e.preventDefault();
                    if (historyIdx < chatHistory.length - 1) {
                        historyIdx++;
                    }
                    ta.value = chatHistory[chatHistory.length - 1 - historyIdx];
                }
                return;
            }

            if (e.key === 'ArrowDown') {
                if (historyIdx > 0) {
                    e.preventDefault();
                    historyIdx--;
                    ta.value = chatHistory[chatHistory.length - 1 - historyIdx];
                } else if (historyIdx === 0) {
                    e.preventDefault();
                    historyIdx = -1;
                    ta.value = '';
                }
                return;
            }

            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const val = ta.value.trim();
                if (val) {
                    chatHistory.push(val);
                    historyIdx = -1;
                }
                if (typeof handleSendMessage === 'function') {
                    handleSendMessage(e);
                }
            }
        });
    });
    </script>
    </body>
    """

    content = content.replace("</body>", fix_script)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Restored clean input binding in: {path}")

