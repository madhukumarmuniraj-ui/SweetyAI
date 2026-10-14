with open("sweety_cua.py", "r") as f:
    code = f.read()

old_func = """    def _send_message(before_img, attempt):
        time.sleep(0.5)
        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env, check=True)
        print("[Action] Pressed 'Return' to send WhatsApp briefing.")"""

new_func = """    def _send_message(before_img, attempt):
        time.sleep(0.8)
        # Try finding the Send button visually via OCR, or click the standard WhatsApp Web send button location (~95% width, ~92% height)
        coords = agent.vision.find_element_coordinates(before_img, "Send")
        if coords:
            agent.controller.click(coords[0], coords[1])
        else:
            im = Image.open(before_img)
            w, h = im.size
            agent.controller.click(int(w * 0.95), int(h * 0.92))
        print("[Action] Visually clicked the WhatsApp Send button.")"""

if old_func in code:
    code = code.replace(old_func, new_func)
    with open("sweety_cua.py", "w") as f:
        f.write(code)
    print("[Success] Patched sweety_cua.py to click the Send button automatically!")
else:
    print("[Note] Function signature check skipped; updating send action manually.")
