import os
import subprocess
import time
import urllib.parse
import argparse

def build_live_diary_briefing():
    return (
        "⚖️ *SWEETYAI DAILY LEGAL BRIEFING* ⚖️\n"
        "----------------------------------------\n"
        "📅 *Date:* Today\n"
        "🏛️ *Court:* High Court of Karnataka / District Courts\n\n"
        "📋 *Active Cause List & Matters:*\n"
        "1. Case No: WP 12345/2026 - Listed for Preliminary Hearing\n"
        "2. Case No: CRL.P 6789/2026 - Interim Stay Extension Active\n\n"
        "⚡ *Priority Alerts:*\n"
        "- Interim stay order verified and logged.\n"
        "- Check physical filing receipts for pending matters.\n\n"
        "_Automated via Arch Linux Workstation_"
    )

def run_local_whatsapp_desktop(phone_number):
    print("\n=== SWEETYAI: UNIVERSAL FOCUS DISPATCH ===")
    clean_phone = "".join(ch for ch in phone_number if ch.isdigit())
    if len(clean_phone) == 10:
        clean_phone = "91" + clean_phone

    briefing = build_live_diary_briefing()
    encoded_briefing = urllib.parse.quote(briefing)

    url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={encoded_briefing}"
    print(f"[Action] Opening WhatsApp Web for +{clean_phone}...")
    subprocess.Popen(["xdg-open", url])

    print("[Action] Waiting 12 seconds for WhatsApp Web to load...")
    time.sleep(12.0)

    geom = subprocess.run(["xdotool", "getdisplaygeometry"], capture_output=True, text=True)
    if geom.returncode == 0 and geom.stdout.strip():
        parts = geom.stdout.strip().split()
        sw, sh = int(parts[0]), int(parts[1])
    else:
        sw, sh = 1360, 768

    box_x = int(sw * 0.60)
    box_y = int(sh * 0.92)

    print(f"[Action] Clicking chat input box at ({box_x}, {box_y})...")
    subprocess.run(["xdotool", "mousemove", str(box_x), str(box_y), "click", "1"])
    time.sleep(0.8)

    print("[Action] Triggering Return key to dispatch...")
    subprocess.run(["xdotool", "key", "Return"])
    time.sleep(0.5)
    subprocess.run(["xdotool", "key", "ctrl+Return"])
    print(f"\n[Success] Dispatch sequence completed for +{clean_phone}!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default="local")
    parser.add_argument("--grant-control", action="store_true")
    parser.add_argument("--task", default="whatsapp")
    parser.add_argument("--target", default="9844637595")
    args = parser.parse_args()
    if args.task == "whatsapp":
        run_local_whatsapp_desktop(args.target)
