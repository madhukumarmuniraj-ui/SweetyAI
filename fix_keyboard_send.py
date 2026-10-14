with open("sweety_cua.py", "r") as f:
    code = f.read()

old_block = """    def _send_message(before_img, attempt):
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

new_block = """    def _send_message(before_img, attempt):
        time.sleep(1.5)
        # WhatsApp Web pre-filled URL parameters require a clean focus and explicit Enter keystrokes to dispatch
        print("[Action] Triggering message dispatch via keyboard submission...")
        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env, check=True)
        time.sleep(0.4)
        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env, check=True)
        print("[Action] Double Return keystroke executed successfully.")"""

if old_block in code:
    code = code.replace(old_block, new_block)
    with open("sweety_cua.py", "w") as f:
        f.write(code)
    print("[Success] Patched sweety_cua.py for keyboard-driven dispatch!")
else:
    print("[Note] Applying manual regex replacement.")
    # Fallback to ensure it updates even if spacing varies
    import re
    code = re.sub(r'def _send_message\(before_img, attempt\):.*?(?=\n    def |\nif __name__)', new_block, code, flags=re.DOTALL)
    with open("sweety_cua.py", "w") as f:
        f.write(code)
    print("[Success] Fallback patch applied.")
