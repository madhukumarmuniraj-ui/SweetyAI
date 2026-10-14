import os

for path in ["/home/madhukumarm/SweetyAI/index.html", "/home/madhukumarm/SweetyAI/dist/index.html"]:
    if not os.path.exists(path):
        continue
        
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # We will update the endpoint URL logic inside handleSendMessage
    # to check if a RAG toggle is active, or default to /rag-chat for deep legal queries
    old_fetch = 'fetch("http://127.0.0.1:8765/chat"'
    new_fetch = '''const isRagMode = document.getElementById('ragToggle') ? document.getElementById('ragToggle').checked : true;
            const endpoint = isRagMode ? "http://127.0.0.1:8765/rag-chat" : "http://127.0.0.1:8765/chat";
            
            fetch(endpoint,'''
            
    if old_fetch in content and "isRagMode" not in content:
        content = content.replace(old_fetch, new_fetch)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Successfully patched RAG endpoint support into: {path}")
    else:
        print(f"RAG endpoint support already present or fetch pattern not found in: {path}")

