with open("sweety_cua.py", "r") as f:
    code = f.read()

old_wf = """def run_local_whatsapp_desktop(agent, phone_or_target):
    print("\\n=== SWEETYAI COMPUTER USE: NATIVE APP WHATSAPP DISPATCH ===")
    briefing = build_live_diary_briefing()

    # 1. Load briefing text into system clipboard
    p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE, env=agent.runtime.env)
    p.communicate(input=briefing.encode("utf-8"))
    print("[Action] Briefing payload loaded into system clipboard.")

    # 2. Launch or focus native WhatsApp desktop client
    print("[Action] Launching / Focusing native WhatsApp Desktop app...")
    res = subprocess.run(["xdotool", "search", "--name", "WhatsApp", "windowactivate"], env=agent.runtime.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if res.returncode != 0:
        subprocess.Popen(["whatsapp-linux-desktop"], env=agent.runtime.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5.0)
    else:
        time.sleep(1.5)

    # 3. Use search shortcut (Ctrl+F) to find the contact or 'Message Yourself'
    def _search_and_dispatch(before_img, attempt):
        # Open search
        subprocess.run(["xdotool", "key", "ctrl+f"], env=agent.runtime.env, check=True)
        time.sleep(0.5)
        
        # Type target phone number or contact name
        subprocess.run(["xdotool", "type", "--delay", "30", phone_or_target], env=agent.runtime.env, check=True)
        time.sleep(1.2)
        
        # Press Enter to open the chat
        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env, check=True)
        time.sleep(1.0)
        
        # Paste the briefing from clipboard
        subprocess.run(["xdotool", "key", "ctrl+v"], env=agent.runtime.env, check=True)
        time.sleep(0.8)
        
        # Press Return to send the message
        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env, check=True)
        print("[Action] Native app search, paste, and send sequence executed.")

    agent.execute_verified_action("Native App Search & Dispatch", _search_and_dispatch)
    print(f"\\n[Success] Native WhatsApp desktop dispatch completed for {phone_or_target}!")"""

new_wf = """def run_local_whatsapp_desktop(agent, phone_or_target):
    print("\\n=== SWEETYAI: ACTIVE WINDOW DISPATCH ===")
    briefing = build_live_diary_briefing()

    # 1. Load briefing text into system clipboard
    p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE, env=agent.runtime.env)
    p.communicate(input=briefing.encode("utf-8"))
    print("[Action] Briefing payload loaded into system clipboard.")

    # 2. Focus any open WhatsApp or browser window containing WhatsApp
    print("[Action] Focusing open WhatsApp window...")
    subprocess.run(["xdotool", "search", "--name", "WhatsApp", "windowactivate"], env=agent.runtime.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)

    # 3. Perform search, paste, and send
    def _active_dispatch(before_img, attempt):
        # Open search bar in WhatsApp
        subprocess.run(["xdotool", "key", "ctrl+f"], env=agent.runtime.env, check=True)
        time.sleep(0.5)
        
        # Type target phone number
        subprocess.run(["xdotool", "type", "--delay", "30", phone_or_target], env=agent.runtime.env, check=True)
        time.sleep(1.2)
        
        # Select chat
        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env, check=True)
        time.sleep(1.0)
        
        # Paste briefing
        subprocess.run(["xdotool", "key", "ctrl+v"], env=agent.runtime.env, check=True)
        time.sleep(0.8)
        
        # Send message
        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env, check=True)
        print("[Action] Active window dispatch sequence executed successfully.")

    agent.execute_verified_action("Active Window Dispatch", _active_dispatch)
    print(f"\\n[Success] Briefing dispatched to {phone_or_target}!")"""

if old_wf in code:
    code = code.replace(old_wf, new_wf)
    with open("sweety_cua.py", "w") as f:
        f.write(code)
    print("[Success] sweety_cua.py updated to use active window focus!")
else:
    print("[Error] Function match failed.")
