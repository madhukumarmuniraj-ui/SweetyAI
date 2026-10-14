with open("sweety_cua.py", "r") as f:
    code = f.read()

import re

new_func_implementation = """def run_local_whatsapp_desktop(agent, phone_or_target):
    print("\\n=== SWEETYAI: DOM-TARGETED WHATSAPP DISPATCH ===")
    clean_phone = "".join(ch for ch in phone_or_target if ch.isdigit())
    if len(clean_phone) == 10:
        clean_phone = "91" + clean_phone

    briefing = build_live_diary_briefing()

    # 1. Load briefing text into system clipboard
    p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE, env=agent.runtime.env)
    p.communicate(input=briefing.encode("utf-8"))
    print("[Action] Briefing payload loaded into system clipboard.")

    # 2. Open clean browser URL for target chat
    url = f"https://web.whatsapp.com/send?phone={clean_phone}"
    print(f"[Action] Opening WhatsApp Web for +{clean_phone}...")
    subprocess.Popen(["xdg-open", url], env=agent.runtime.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("[Vision] Waiting 12 seconds for WhatsApp Web DOM to fully initialize...")
    time.sleep(12.0)

    def _dom_paste_and_send(before_img, attempt):
        # Use OCR/Vision to find the exact input box labeled or containing placeholder text, or click center-bottom reliably
        coords = agent.vision.find_element_coordinates(before_img, "Type a message")
        if not coords:
            coords = agent.vision.find_element_coordinates(before_img, "Type")
        
        if coords:
            print(f"[Vision] Located message box via OCR at {coords}")
            agent.controller.click(coords[0], coords[1])
        else:
            im = Image.open(before_img)
            w, h = im.size
            # Fallback to precise chat box input area
            agent.controller.click(int(w * 0.55), int(h * 0.92))
            
        time.sleep(0.6)
        # Paste clipboard content
        subprocess.run(["xdotool", "key", "ctrl+v"], env=agent.runtime.env, check=True)
        print("[Action] Pasted briefing into chat box.")
        time.sleep(0.8)
        
        # Send message via Return key
        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env, check=True)
        print("[Action] Dispatched message via Return key.")

    agent.execute_verified_action("DOM-Targeted Dispatch", _dom_paste_and_send)
    print(f"\\n[Success] WhatsApp dispatch routine completed for +{clean_phone}!")
"""

code = re.sub(r'def run_local_whatsapp_desktop\(.*?\n(?=\ndef |\nif __name__|$)', new_func_implementation, code, flags=re.DOTALL)

with open("sweety_cua.py", "w") as f:
    f.write(code)

print("[Success] sweety_cua.py updated with DOM-targeted element matching!")
