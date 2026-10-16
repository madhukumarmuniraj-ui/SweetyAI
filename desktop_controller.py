"""
SweetyAI Desktop Automation Controller (Wayland Compatible)
Enables mouse movement, automated keyboard typing, and screen capture.
"""

import time
import subprocess
import pyautogui

pyautogui.FAILSAFE = True

def type_legal_document(text_content):
    """Clicks into an active text editor and types out a draft automatically."""
    print("[SweetyAI Desktop] Preparing to type in 3 seconds... Focus your text editor!")
    time.sleep(3)
    
    print("[SweetyAI Desktop] Typing draft text...")
    pyautogui.write(text_content, interval=0.02)
    print("[SweetyAI Desktop] Typing complete.")

def capture_screen():
    """Takes a snapshot of the current workstation screen using Wayland's grim tool."""
    filename = "workstation_snapshot.png"
    try:
        subprocess.run(["grim", filename], check=True)
        print(f"[SweetyAI Desktop] Screen successfully captured and saved as {filename}")
    except Exception as e:
        print(f"[SweetyAI Desktop] Error capturing screen via Wayland: {e}")

if __name__ == "__main__":
    print("Testing SweetyAI Desktop Controller on Wayland...")
    capture_screen()
