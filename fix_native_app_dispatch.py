with open("sweety_cua.py", "r") as f:
    code = f.read()

old_wf = """def run_local_whatsapp_desktop(agent, phone_or_target):
    print("\\n=== SWEETYAI COMPUTER USE: CLIPBOARD-BASED WHATSAPP DISPATCH ===")
    clean_phone = "".join(ch for ch in phone_or_target if ch.isdigit())
    if not clean_phone:
        clean_phone = "919845000003"
    elif len(clean_phone) == 10:
        clean_phone = "91" + clean_phone

    briefing = build_live_diary_briefing()

    # 1. Load briefing text directly into Linux clipboard
    p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE, env=agent.runtime.env)
    p.communicate(input=briefing.encode("utf-8"))
    print("[Action] Briefing payload loaded into system clipboard.")

    # 2. Open clean chat URL (no unreliable URL text parameter)
    url = f"https://web.whatsapp.com/send?phone={clean_phone}"
    print(f"[Action] Opening clean WhatsApp Web URL for +{clean_phone}...")
    subprocess.Popen(["xdg-open", url], env=agent.runtime.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("[Vision] Waiting 10 seconds for WhatsApp Web to render chat session...")
    time.sleep(10.0)

    # 3. Focus chat input box and paste clipboard contents
    def _paste_and_send(before_img, attempt):
        im = Image.open(before_img)
        w, h = im.size
        # Click center-bottom input area to guarantee focus
        agent.controller.click(int(w * 0.60), int(h * 0.92))
        time.sleep(0.5)

        # Send Ctrl+V to paste briefing
        subprocess.run(["xdotool", "key", "ctrl+v"], env=agent.runtime.env, check=True)
        print("[Action] Pasted briefing payload from clipboard.")
        time.sleep(0.8)

        # Press Return to send
        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env, check=True)
        print("[Action] Sent dispatch Return keystroke.")

    agent.execute_verified_action("Paste & Send Court Briefing", _paste_and_send)
    print(f"\\n[Success] Clipboard-based WhatsApp message successfully delivered to +{clean_phone}!")"""

new_wf = """def run_local_whatsapp_desktop(agent, phone_or_target):
    print("\\n=== SWEETYAI COMPUTER USE: NATIVE APP WHATSAPP DISPATCH ===")
    briefing = build_live_diary_briefing()

    # 1. Load briefing text into system clipboard
    p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE, env=agent.runtime.env)
    p.communicate(input=briefing.encode("utf-8"))
    print("[Action] Briefing payload loaded into system clipboard.")

    # 2. Launch or activate native WhatsApp desktop client
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

if old_wf in code:
    code = code.replace(old_wf, new_wf)
    with open("sweety_cua.py", "w") as f:
        f.write(code)
    print("[Success] Updated sweety_cua.py to use native whatsapp-linux-desktop!")
else:
    print("[Error] Function block match failed. Please check script.")
