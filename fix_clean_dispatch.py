import re

with open("sweety_cua.py", "r") as f:
    code = f.read()

new_func_implementation = """def run_local_whatsapp_desktop(agent, phone_or_target):
    print("\\n=== SWEETYAI: SAFE CLIPBOARD DISPATCH ===")
    clean_phone = "".join(ch for ch in phone_or_target if ch.isdigit())
    if len(clean_phone) == 10:
        clean_phone = "91" + clean_phone

    briefing = build_live_diary_briefing()

    # Load briefing text into system clipboard
    p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE, env=agent.runtime.env)
    p.communicate(input=briefing.encode("utf-8"))
    print("[Action] Briefing payload loaded into system clipboard.")

    # Open clean browser URL for target chat
    url = f"https://web.whatsapp.com/send?phone={clean_phone}"
    print(f"[Action] Opening WhatsApp Web for +{clean_phone}...")
    subprocess.Popen(["xdg-open", url], env=agent.runtime.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("[Vision] Waiting 8 seconds for chat to render...")
    time.sleep(8.0)

    def _paste_and_send(before_img, attempt):
        im = Image.open(before_img)
        w, h = im.size
        # Click chat input box
        agent.controller.click(int(w * 0.60), int(h * 0.92))
        time.sleep(0.4)
        # Paste clipboard content
        subprocess.run(["xdotool", "key", "ctrl+v"], env=agent.runtime.env, check=True)
        time.sleep(0.6)
        # Send message
        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env, check=True)
        print("[Action] Briefing pasted and dispatched successfully.")

    agent.execute_verified_action("Safe Clipboard Dispatch", _paste_and_send)
    print(f"\\n[Success] WhatsApp dispatch completed for +{clean_phone}!")
"""

# Use re.DOTALL properly with the re module
code = re.sub(r'def run_local_whatsapp_desktop\(.*?\n(?=\ndef |\nif __name__|$)', new_func_implementation, code, flags=re.DOTALL)

with open("sweety_cua.py", "w") as f:
    f.write(code)

print("[Success] sweety_cua.py successfully updated!")
