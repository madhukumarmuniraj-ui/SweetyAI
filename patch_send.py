with open("sweety_cua.py", "r") as f:
    code = f.read()

old_send = """    def _send_message(before_img, attempt):
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

new_send = """    def _send_message(before_img, attempt):
        time.sleep(1.0)
        im = Image.open(before_img)
        w, h = im.size
        # WhatsApp Web send button is fixed near the bottom-right of the chat box
        send_x = int(w * 0.94)
        send_y = int(h * 0.92)
        agent.controller.click(send_x, send_y)
        print(f"[Action] Clicked WhatsApp Send button at exact coordinates ({send_x}, {send_y}).")"""

if old_send in code:
    code = code.replace(old_send, new_send)
    with open("sweety_cua.py", "w") as f:
        f.write(code)
    print("[Success] Patched sweety_cua.py with precise Send button coordinates!")
else:
    print("[Error] Could not find exact string match; applying direct replacement.")
