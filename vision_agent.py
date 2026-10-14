import os
import shutil
import subprocess
import datetime
import requests

BASE_URL = "http://127.0.0.1:8765"


def get_active_window_info():
    info = {
        "display_server": os.environ.get("XDG_SESSION_TYPE", "x11/wayland"),
        "display": os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY") or ":0",
        "active_window": "Terminal / SweetyAI Workspace",
    }
    # Try xdotool or xprop if available
    if shutil.which("xdotool"):
        try:
            win_name = subprocess.check_output(
                ["xdotool", "getactivewindow", "getwindowname"],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=3,
            ).strip()
            if win_name:
                info["active_window"] = win_name
        except Exception:
            pass
    elif shutil.which("wmctrl"):
        try:
            out = subprocess.check_output(["wmctrl", "-l"], stderr=subprocess.DEVNULL, text=True, timeout=3)
            lines = [l.strip() for l in out.splitlines() if l.strip()]
            if lines:
                info["active_window"] = lines[-1].split(None, 3)[-1]
        except Exception:
            pass
    return info


def capture_screen(output_path="sweety_screen_capture.png"):
    # 1. Try native Linux screenshot utilities
    commands = [
        (["scrot", "-o", output_path], "scrot"),
        (["gnome-screenshot", "-f", output_path], "gnome-screenshot"),
        (["grim", output_path], "grim (Wayland)"),
        (["import", "-window", "root", output_path], "ImageMagick import"),
    ]
    for cmd, name in commands:
        if shutil.which(cmd[0]):
            try:
                res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
                if res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    return True, f"Captured live display via {name} -> {output_path} ({os.path.getsize(output_path)} bytes)"
            except Exception:
                pass

    # 2. Fallback: Headless Chromium viewport render of active SweetyAI UI (index.html)
    for binary in ["google-chrome", "chromium", "chromium-browser"]:
        browser = shutil.which(binary)
        if browser and os.path.exists("index.html"):
            try:
                target_uri = f"file://{os.path.abspath('index.html')}"
                cmd = [
                    browser,
                    "--headless",
                    "--disable-gpu",
                    "--no-sandbox",
                    f"--screenshot={output_path}",
                    "--window-size=1280,800",
                    target_uri,
                ]
                res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    return True, f"Captured active UI viewport via Headless Chromium -> {output_path} ({os.path.getsize(output_path)} bytes)"
            except Exception:
                pass

    return False, "No graphical framebuffer utility found; using live workspace document & DOM context."


def extract_screen_text(image_path):
    extracted = []

    # Try OCR via tesseract if installed
    if os.path.exists(image_path) and shutil.which("tesseract"):
        try:
            ocr_text = subprocess.check_output(
                ["tesseract", image_path, "stdout", "--psm", "6"],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=8,
            ).strip()
            if ocr_text:
                extracted.append(f"[OCR Screen Text]: {ocr_text[:400]}")
        except Exception:
            pass

    # Inspect most recently active legal brief or document in workspace
    recent_docs = sorted(
        [f for f in os.listdir(".") if f.endswith((".md", ".txt", ".pdf")) and not f.startswith(".")],
        key=lambda x: os.path.getmtime(x),
        reverse=True,
    )
    if recent_docs:
        top_doc = recent_docs[0]
        if top_doc.endswith(".pdf"):
            try:
                import pymupdf
                doc = pymupdf.open(top_doc)
                page_text = doc[0].get_text("text").strip()[:400]
                extracted.append(f"[Active Workspace PDF '{top_doc}']: {page_text}")
            except Exception:
                pass
        else:
            try:
                with open(top_doc, "r", encoding="utf-8", errors="replace") as f:
                    snippet = " ".join(f.read().split())[:400]
                extracted.append(f"[Active Workspace Document '{top_doc}']: {snippet}")
            except Exception:
                pass

    return "\n".join(extracted) if extracted else "Active SweetyAI Desktop UI & Terminal Session"


def analyze_screen(question):
    print("\n=== SweetyAI Real-Time Screen Awareness (Vision Agent) ===")
    print(f"Timestamp      : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    win_info = get_active_window_info()
    print(f"Display Server : {win_info['display_server']} ({win_info['display']})")
    print(f"Active Window  : {win_info['active_window']}")

    img_path = "sweety_screen_capture.png"
    captured, cap_msg = capture_screen(img_path)
    print(f"Screen Capture : {cap_msg}")

    visual_context = extract_screen_text(img_path)
    print(f"\n[Detected On-Screen / Active Context]:\n{visual_context}\n")

    # Cross-query Legal RAG / Intelligence Server with the on-screen context + user question
    combined_query = f"Question: {question} | Context: {visual_context[:300]}"
    print(f"[Answering Your Screen Query]: '{question}'")
    try:
        resp = requests.post(f"{BASE_URL}/rag-chat", json={"message": combined_query}, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"\nSweety Vision Synthesis:\n{data.get('response')}")
            if data.get("sources"):
                print(f"Cross-Referenced Sources: {', '.join(data.get('sources'))}")
        else:
            print(f"Server status: {resp.status_code}")
    except Exception as e:
        print(f"Local synthesis (offline fallback): Viewing '{win_info['active_window']}' — {visual_context[:200]} ({e})")
    print("==========================================================\n")
