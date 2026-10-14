with open("sweety_cua.py", "r") as f:
    code = f.read()

old_send = """    def _send_message(before_img, attempt):
        time.sleep(1.0)
        im = Image.open(before_img)
        w, h = im.size
        # WhatsApp Web send button is fixed near the bottom-right of the chat box
        send_x = int(w * 0.94)
        send_y = int(h * 0.92)
        agent.controller.click(send_x, send_y)
        print(f"[Action] Clicked WhatsApp Send button at exact coordinates ({send_x}, {send_y}).")"""

new_send = """    def _send_message(before_img, attempt):
        time.sleep(1.0)
        im = Image.open(before_img)
        w, h = im.size
        # Force exact bottom-right position of the WhatsApp Web chat box
        send_x = int(w * 0.94)
        send_y = int(h * 0.92)
        # Press Enter first to lock text input, then click the send icon
        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env)
        time.sleep(0.3)
        agent.controller.click(send_x, send_y)
        print(f"[Action] Clicked WhatsApp Send button at exact coordinates ({send_x}, {send_y}).")"""

if old_send in code:
    code = code.replace(old_send, new_send)
    with open("sweety_cua.py", "w") as f:
        f.write(code)
    print("[Success] sweety_cua.py patched with bulletproof Send button logic!")
else:
    print("[Error] Manual check needed.")
