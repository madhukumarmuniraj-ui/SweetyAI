with open("sweety_cua.py", "r") as f:
    code = f.read()

old_wf = """def run_local_whatsapp_desktop(agent, phone_or_target):
    print("\\n=== SWEETYAI COMPUTER USE: LIVE LOCAL WHATSAPP DISPATCH ===")
    clean_phone = "".join(ch for ch in phone_or_target if ch.isdigit())
    if not clean_phone:
        clean_phone = "919845000003"
    elif len(clean_phone) == 10:
        clean_phone = "91" + clean_phone

    briefing = build_live_diary_briefing()
    encoded_text = urllib.parse.quote(briefing)
    url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={encoded_text}"

    print(f"[Action] Opening WhatsApp Web direct dispatch URL for +{clean_phone}...")
    subprocess.Popen(["xdg-open", url], env=agent.runtime.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("[Vision] Waiting 12 seconds for WhatsApp Web chat interface to load...")
    time.sleep(12.0)

    def _focus_chat_input(before_img, attempt):
        coords = agent.vision.find_element_coordinates(before_img, "Type")
        if coords:
            agent.controller.click(coords[0], coords[1])
        else:
            im = Image.open(before_img)
            w, h = im.size
            agent.controller.click(int(w * 0.60), int(h * 0.92))

    agent.execute_verified_action("Focus WhatsApp Web Message Box", _focus_chat_input)

    def _send_message(before_img, attempt):
        time.sleep(1.5)
        # WhatsApp Web pre-filled URL parameters require a clean focus and explicit Enter keystrokes to dispatch
        print("[Action] Triggering message dispatch via keyboard submission...")
        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env, check=True)
        time.sleep(0.4)
        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env, check=True)
        print("[Action] Double Return keystroke executed successfully.")

    agent.execute_verified_action("Send Pre-Filled Court Briefing", _send_message)
    print(f"\\n[Success] Live WhatsApp message physically dispatched to +{clean_phone}!")"""

new_wf = """def run_local_whatsapp_desktop(agent, phone_or_target):
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

if old_wf in code:
    code = code.replace(old_wf, new_wf)
    with open("sweety_cua.py", "w") as f:
        f.write(code)
    print("[Success] sweety_cua.py updated with robust clipboard injection workflow!")
else:
    print("[Error] Function block mismatch. Please check script structure.")
