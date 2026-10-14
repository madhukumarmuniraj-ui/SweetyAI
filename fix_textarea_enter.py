import os
import re

for path in ["/home/madhukumarm/SweetyAI/index.html", "/home/madhukumarm/SweetyAI/dist/index.html"]:
    if not os.path.exists(path):
        continue
        
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Find the textarea tag and ensure it has id="textarea" and the onkeydown handler
    # We will replace any existing textarea tag or insert the handler
    if "<textarea" in content:
        # Use regex to find the textarea tag
        def add_handler(match):
            tag = match.group(0)
            if "onkeydown" not in tag:
                # Insert onkeydown right before the closing > of the opening tag
                tag = tag[:-1] + ' onkeydown="if(event.key === \'Enter\' && !event.shiftKey) { event.preventDefault(); handleSendMessage(event); }">'
            if 'id="textarea"' not in tag and "id='textarea'" not in tag:
                tag = tag.replace("<textarea", '<textarea id="textarea"')
            return tag
            
        content = re.sub(r'<textarea[^>]*>', add_handler, content)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Successfully added direct Enter key handler to textarea in: {path}")

