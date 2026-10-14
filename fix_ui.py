import os
import re

paths = ["/home/madhukumarm/SweetyAI/index.html", "/home/madhukumarm/SweetyAI/dist/index.html"]

for path in paths:
    if not os.path.exists(path):
        continue
        
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # The new function that actually connects to port 8765
    new_func = """function handleSendMessage(event) {
            event.preventDefault();
            const message = textarea.value.trim();
            if (!message) return;

            if (chatContainer.querySelector('h1')) {
                chatContainer.innerHTML = '';
            }

            const userBubble = document.createElement('div');
            userBubble.className = 'max-w-3xl mx-auto flex gap-4 px-4';
            userBubble.innerHTML = `<div class="w-8 h-8 rounded-full bg-indigo-600 flex-shrink-0 flex items-center justify-center font-bold text-sm">U</div><div class="flex-1 space-y-1 text-gray-200 text-sm leading-relaxed whitespace-pre-wrap">${escapeHtml(message)}</div>`;
            chatContainer.appendChild(userBubble);

            textarea.value = '';
            textarea.style.height = 'auto';
            sendBtn.disabled = true;
            chatContainer.scrollTop = chatContainer.scrollHeight;

            fetch("http://127.0.0.1:8765/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: message })
            })
            .then(res => res.json())
            .then(data => {
                sendBtn.disabled = false;
                const aiBubble = document.createElement('div');
                aiBubble.className = 'max-w-3xl mx-auto flex gap-4 px-4 bg-[#2a2a2a]/50 py-4 rounded-xl';
                const replyText = data.response || data.reply || data.answer || JSON.stringify(data);
                aiBubble.innerHTML = `<div class="w-8 h-8 rounded-full bg-emerald-600 flex-shrink-0 flex items-center justify-center font-bold text-sm">S</div><div class="flex-1 space-y-1 text-gray-200 text-sm leading-relaxed">${escapeHtml(replyText)}</div>`;
                chatContainer.appendChild(aiBubble);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            })
            .catch(error => {
                sendBtn.disabled = false;
                const errBubble = document.createElement('div');
                errBubble.className = 'max-w-3xl mx-auto flex gap-4 px-4 bg-red-900/50 py-4 rounded-xl';
                errBubble.innerHTML = `<div class="flex-1 text-red-200 text-sm">Backend Connection Error: Cannot reach the Python server.</div>`;
                chatContainer.appendChild(errBubble);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            });
        }"""
        
    # Replace the broken function with the working one
    content = re.sub(r"function handleSendMessage\(event\)\s*\{.*?(?=\n\s*function escapeHtml)", new_func, content, flags=re.DOTALL)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Fixed UI connection in: {path}")

