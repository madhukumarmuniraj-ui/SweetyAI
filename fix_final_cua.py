with open("sweety_cua.py", "r") as f:
    code = f.read()

old_func = """def run_local_whatsapp_desktop(agent, phone_or_target):
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

new_func = """def run_local_whatsapp_desktop(agent, phone_or_target):
    print("\\n=== SWEETYAI: ROBUST BROWSER URL DISPATCH ===")
    clean_phone = "".join(ch for ch in phone_or_target if ch.isdigit())
    if len(clean_phone) == 10:
        clean_phone = "91" + clean_phone

    briefing = build_live_diary_briefing()
    encoded_text = urllib.parse.quote(briefing)
    
    url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={encoded_text}"
    print(f"[Action] Opening browser for dispatch to +{clean_phone}...")
    subprocess.Popen(["xdg-open", url], env=agent.runtime.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("[Vision] Waiting 10 seconds for WhatsApp Web to load...")
    time.sleep(10.0)

    def _press_enter(before_img, attempt):
        print("[Action] Sending Enter keystroke to trigger message send...")
        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env, check=True)
        time.sleep(0.4)
        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env, check=True)

    agent.execute_verified_action("Browser Send Confirmation", _press_enter)
    print(f"\\n[Success] WhatsApp briefing URL successfully opened and dispatched for +{clean_phone}!")"""

if old_func in code:
    code = code.replace(old_func, new_func)
    with open("sweety_cua.py", "w") as f:
        f.write(code)
    print("[Success] Patched sweety_cua.py to use robust browser URL dispatch!")
else:
    print("[Error] Function replacement failed.")
