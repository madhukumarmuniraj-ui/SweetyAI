import os

paths = ["/home/madhukumarm/SweetyAI/index.html", "/home/madhukumarm/SweetyAI/dist/index.html"]

for path in paths:
    if not os.path.exists(path):
        continue
        
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Define a clean handleKeyDown implementation that supports Enter to send and Up/Down for history
    new_key_handler = """
    <script>
    let globalMessageHistory = [];
    let globalHistoryIndex = -1;

    function handleKeyDown(event) {
        const ta = document.getElementById('textarea');
        if (!ta) return;

        if (event.key === 'ArrowUp') {
            if (globalMessageHistory.length > 0) {
                event.preventDefault();
                if (globalHistoryIndex < globalMessageHistory.length - 1) {
                    globalHistoryIndex++;
                }
                ta.value = globalMessageHistory[globalMessageHistory.length - 1 - globalHistoryIndex];
            }
            return;
        }

        if (event.key === 'ArrowDown') {
            if (globalHistoryIndex > 0) {
                event.preventDefault();
                globalHistoryIndex--;
                ta.value = globalMessageHistory[globalMessageHistory.length - 1 - globalHistoryIndex];
            } else if (globalHistoryIndex === 0) {
                event.preventDefault();
                globalHistoryIndex = -1;
                ta.value = '';
            }
            return;
        }

        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            const text = ta.value.trim();
            if (text) {
                globalMessageHistory.push(text);
                globalHistoryIndex = -1;
            }
            if (typeof handleSendMessage === 'function') {
                handleSendMessage(event);
            }
        }
    }
    </script>
    </body>
    """

    # Clean up duplicate script injections if any exist and append our clean handler
    if "globalMessageHistory" not in content:
        content = content.replace("</body>", new_key_handler)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Cleaned and patched textarea handler in: {path}")

