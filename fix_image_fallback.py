with open("sweety_cua.py", "r") as f:
    content = f.read()

old_paste = '''    def _paste_and_send(before_img, attempt):
        im = Image.open(before_img)
        w, h = im.size
        # Click chat input box cleanly
        agent.controller.click(int(w * 0.60), int(h * 0.92))
        time.sleep(0.4)
        # Paste clipboard content
        subprocess.run(["xdotool", "key", "ctrl+v"], env=agent.runtime.env, check=True)
        time.sleep(0.6)
        # Send message
        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env, check=True)
        print("[Action] Briefing pasted and dispatched successfully.")'''

new_paste = '''    def _paste_and_send(before_img, attempt):
        if before_img:
            im = Image.open(before_img)
            w, h = im.size
        else:
            w, h = 1920, 1080  # Default fallback resolution
        
        # Click chat input box cleanly
        agent.controller.click(int(w * 0.60), int(h * 0.92))
        time.sleep(0.4)
        # Paste clipboard content
        subprocess.run(["xdotool", "key", "ctrl+v"], env=agent.runtime.env, check=True)
        time.sleep(0.6)
        # Send message
        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env, check=True)
        print("[Action] Briefing pasted and dispatched successfully.")'''

if old_paste in content:
    content = content.replace(old_paste, new_paste)
    with open("sweety_cua.py", "w") as f:
        f.write(content)
    print("[Success] sweety_cua.py updated with image fallback!")
else:
    print("[Warning] Exact match not found, updating via regex.")
    import re
    content = re.sub(r'def _paste_and_send\(before_img, attempt\):.*?(?=    agent\.execute_verified_action)', new_paste + '\n\n    ', content, flags=re.DOTALL)
    with open("sweety_cua.py", "w") as f:
        f.write(content)
    print("[Success] sweety_cua.py updated via regex fallback!")
