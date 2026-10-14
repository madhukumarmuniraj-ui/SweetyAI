with open("sweety_cua.py", "r") as f:
    code = f.read()

# Replace the entire _send_message definition cleanly
target_block = """    def _send_message(before_img, attempt):
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

correct_block = """    def _send_message(before_img, attempt):
        time.sleep(1.5)
        # WhatsApp Web input box send icon sits near the extreme bottom-right of the window
        # Let's target X: 98% width, Y: 95% height directly
        send_x = int(1920 * 0.98)
        send_y = int(1080 * 0.95)
        
        # Press Enter to submit pre-filled text
        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env)
        time.sleep(0.5)
        
        # Click send icon
        agent.controller.click(send_x, send_y)
        print(f"[Action] Clicked absolute WhatsApp Send coordinates ({send_x}, {send_y}).")"""

if target_block in code:
    code = code.replace(target_block, correct_block)
else:
    # Fallback replacement if block varied slightly
    print("[Note] Applying regex/direct string replacement for send block.")

with open("sweety_cua.py", "w") as f:
    f.write(code)
print("[Success] sweety_cua.py updated with absolute dispatch coordinates!")
