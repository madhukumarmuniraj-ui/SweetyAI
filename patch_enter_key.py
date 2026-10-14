import os

for path in ["/home/madhukumarm/SweetyAI/index.html", "/home/madhukumarm/SweetyAI/dist/index.html"]:
    if not os.path.exists(path):
        continue
        
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check if textarea event listener for Enter is already added
    if "textarea.addEventListener('keydown'" not in content:
        # Find where textarea is defined or right before closing </script>
        target = "</script>"
        listener_code = """
        // Added Enter key handler
        document.addEventListener('DOMContentLoaded', () => {
            const ta = document.getElementById('textarea') || document.querySelector('textarea');
            if (ta) {
                ta.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        if (typeof handleSendMessage === 'function') {
                            handleSendMessage(e);
                        } else if (typeof sendMessage === 'function') {
                            sendMessage();
                        }
                    }
                });
            }
        });
        </script>
        """
        content = content.replace(target, listener_code)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Patched Enter key handler into: {path}")
    else:
        print(f"Enter key handler already present in: {path}")

