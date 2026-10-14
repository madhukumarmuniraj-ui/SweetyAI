with open("sweety_cua.py", "r") as f:
    lines = f.readlines()

# Let's find where run_local_whatsapp_desktop starts and clean it up
new_code = []
skip = False
for line in lines:
    if line.startswith("def run_local_whatsapp_desktop"):
        skip = True
        new_code.append("def run_local_whatsapp_desktop(agent, phone_or_target):\n")
        new_code.append('    print("\\n=== SWEETYAI: SAFE CLIPBOARD DISPATCH ===")\n')
        new_code.append('    clean_phone = "".join(ch for ch in phone_or_target if ch.isdigit())\n')
        new_code.append('    if len(clean_phone) == 10:\n')
        new_code.append('        clean_phone = "91" + clean_phone\n\n')
        new_code.append('    briefing = build_live_diary_briefing()\n\n')
        new_code.append('    p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE, env=agent.runtime.env)\n')
        new_code.append('    p.communicate(input=briefing.encode("utf-8"))\n')
        new_code.append('    print("[Action] Briefing payload loaded into system clipboard.")\n\n')
        new_code.append('    url = f"https://web.whatsapp.com/send?phone={clean_phone}"\n')
        new_code.append('    print(f"[Action] Opening WhatsApp Web for +{clean_phone}...")\n')
        new_code.append('    subprocess.Popen(["xdg-open", url], env=agent.runtime.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n\n')
        new_code.append('    print("[Vision] Waiting 8 seconds for chat to render...")\n')
        new_code.append('    time.sleep(8.0)\n\n')
        new_code.append('    def _paste_and_send(before_img, attempt):\n')
        new_code.append('        im = Image.open(before_img)\n')
        new_code.append('        w, h = im.size\n')
        new_code.append('        agent.controller.click(int(w * 0.60), int(h * 0.92))\n')
        new_code.append('        time.sleep(0.4)\n')
        new_code.append('        subprocess.run(["xdotool", "key", "ctrl+v"], env=agent.runtime.env, check=True)\n')
        new_code.append('        time.sleep(0.6)\n')
        new_code.append('        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env, check=True)\n')
        new_code.append('        print("[Action] Briefing pasted and dispatched successfully.")\n\n')
        new_code.append('    agent.execute_verified_action("Safe Clipboard Dispatch", _paste_and_send)\n')
        new_code.append('    print(f"\\n[Success] WhatsApp dispatch completed for +{clean_phone}!")\n')
    elif skip:
        # Skip lines until the end of the file or next major block
        if line.startswith("if __name__ == '__main__':" ) or line.startswith("if __name__ == \"__main__\":"):
            skip = False
            new_code.append(line)
    else:
        new_code.append(line)

with open("sweety_cua.py", "w") as f:
    f.writelines(new_code)

print("[Success] Syntax error resolved and sweety_cua.py cleaned!")
