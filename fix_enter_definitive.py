import os
import re

paths = ["/home/madhukumarm/SweetyAI/index.html", "/home/madhukumarm/SweetyAI/dist/index.html"]

for path in paths:
    if not os.path.exists(path):
        continue
        
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Ensure there is a robust global keydown listener at the bottom of the script
    script_fix = """
    <script>
    // Robust Enter-key handler for SweetyAI
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            const activeEl = document.activeElement;
            if (activeEl && (activeEl.tagName === 'TEXTAREA' || activeEl.id === 'chat-input' || activeEl.id === 'textarea')) {
                event.preventDefault();
                if (typeof handleSendMessage === 'function') {
                    handleSendMessage(event);
                } else if (typeof sendMessage === 'function') {
                    sendMessage();
                } else {
                    const sendBtn = document.getElementById('send-btn') || document.getElementById('sendBtn');
                    if (sendBtn) sendBtn.click();
                }
            }
        }
    });
    </script>
    </body>
    """
    
    if "Robust Enter-key handler" not in content:
        content = content.replace("</body>", script_fix)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Successfully added global Enter listener to: {path}")
    else:
        print(f"Global Enter listener already present in: {path}")

