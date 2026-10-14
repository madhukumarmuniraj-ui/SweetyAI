with open("sweety_cua.py", "r") as f:
    code = f.read()

new_func = '''def run_local_whatsapp_desktop(agent, phone_or_target):
    print("\\n=== SWEETYAI: URL-ENCODED WHATSAPP DISPATCH ===")
    clean_phone = "".join(ch for ch in phone_or_target if ch.isdigit())
    if len(clean_phone) == 10:
        clean_phone = "91" + clean_phone

    briefing = build_live_diary_briefing()
    
    # URL encode the briefing text so it safely populates the chat box via URL parameter
    encoded_briefing = urllib.parse.quote(briefing)

    # Open WhatsApp Web URL with pre-filled text
    url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={encoded_briefing}"
    print(f"[Action] Opening WhatsApp Web with pre-filled briefing for +{clean_phone}...")
    subprocess.Popen(["xdg-open", url], env=agent.runtime.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("[Vision] Waiting 10 seconds for WhatsApp Web to load and render chat...")
    time.sleep(10.0)

    def _press_send(before_img, attempt):
        # Press Return key to dispatch the pre-filled message
        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env, check=True)
        print("[Action] Return key triggered. Briefing dispatched successfully.")

    agent.execute_verified_action("URL-Encoded Dispatch", _press_send)
    print(f"\\n[Success] WhatsApp dispatch completed for +{clean_phone}!")'''

import re
if "def run_local_whatsapp_desktop" in code:
    code = re.sub(r'def run_local_whatsapp_desktop\(.*?(?=\ndef |\nif __name__|$)', new_func + "\n\n", code, flags=re.DOTALL)
else:
    code += "\n\n" + new_func

with open("sweety_cua.py", "w") as f:
    f.write(code)

print("[Success] sweety_cua.py updated to URL-encoded dispatch!")
