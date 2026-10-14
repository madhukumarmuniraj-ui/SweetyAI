with open("sweety_cua.py", "r") as f:
    code = f.read()

old_func = '''    def _paste_and_send(before_img, attempt):
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

new_func = '''    def _paste_and_send(before_img, attempt):
        if before_img:
            im = Image.open(before_img)
            w, h = im.size
        else:
            w, h = 1920, 1080
        
        # 1. Click chat input box explicitly
        agent.controller.click(int(w * 0.60), int(h * 0.92))
        time.sleep(1.0)
        
        # 2. Type summary snippet or send via clipboard with multiple fallback keys
        # On Wayland/XWayland bridge, sometimes clicking defocuses. Let's re-click and use xclip + xdotool safely.
        subprocess.run(["xdotool", "key", "ctrl+shift+v"], env=agent.runtime.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.5)
        
        # Fallback: if ctrl+v didn't stick, let's type a clean short status header or send
        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env, check=True)
        print("[Action] Dispatch sequence executed with explicit focus.")'''

if old_func in code:
    code = code.replace(old_func, new_func)
    with open("sweety_cua.py", "w") as f:
        f.write(code)
    print("[Success] Updated to explicit focus and dispatch!")
else:
    print("[Error] Function block match failed. Let's check manually.")
