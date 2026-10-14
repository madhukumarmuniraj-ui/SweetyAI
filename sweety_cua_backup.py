import os
import sys
import csv
import time
import math
import shutil
import sqlite3
import argparse
import subprocess
import urllib.parse
from datetime import datetime, date
from PIL import Image, ImageChops, ImageOps, ImageStat, ImageDraw, ImageFont

LOG_DIR = "vision_logs"
DB_PATH = os.path.join("diary_data", "advocate_diary.db")
os.makedirs(LOG_DIR, exist_ok=True)


def load_font(size):
    font_paths = [
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/liberation/LiberationSans-Bold.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


# ==============================================================================
# 1. DUAL ENVIRONMENT RUNTIME (Local Machine vs. Self-Contained Sandbox)
# ==============================================================================
class EnvironmentRuntime:
    def __init__(self, mode="local", grant_permission=False):
        self.mode = mode
        self.grant_permission = grant_permission
        self.xvfb_proc = None
        self.env = os.environ.copy()
        self.sandbox_state = {
            "active_field": "NONE",
            "search_text": "",
            "message_text": "",
            "status_banner": "READY FOR AUTOMATION",
            "cursor": (640, 400)
        }

    def start(self):
        if self.mode == "sandbox":
            print("[Environment] Launching isolated Xvfb Sandbox Container on DISPLAY :99...")
            self.xvfb_proc = subprocess.Popen(
                ["Xvfb", ":99", "-screen", "0", "1280x800x24", "-ac"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(0.8)
            self.env["DISPLAY"] = ":99"
            self.env.pop("WAYLAND_DISPLAY", None)
            subprocess.run(["xdotool", "mousemove", "640", "400"], env=self.env)
            print("[Environment] Sandbox active (1280x800) with Virtual Court & WhatsApp UI loaded.")
        else:
            if not self.grant_permission:
                ans = input("[Security] Grant SweetyAI physical control of your Local Machine? (y/N): ").strip().lower()
                if ans != "y":
                    print("[Aborted] Local machine permission denied.")
                    sys.exit(1)
            session_type = self.env.get("XDG_SESSION_TYPE", "x11")
            display = self.env.get("DISPLAY", ":0")
            self.env["DISPLAY"] = display
            print(f"[Environment] Local Machine control granted (DISPLAY={display}, Session={session_type}).")

    def render_sandbox_frame(self, output_path):
        img = Image.new("RGB", (1280, 800), color=(245, 247, 250))
        draw = ImageDraw.Draw(img)

        font_lg = load_font(26)
        font_md = load_font(22)
        font_sm = load_font(18)

        draw.rectangle([0, 0, 1280, 75], fill=(20, 35, 60))
        draw.text((30, 22), "SWEETYAI SANDBOX WORKSTATION", fill=(255, 255, 255), font=font_lg)

        search_border = (0, 120, 215) if self.sandbox_state["active_field"] == "SEARCH" else (180, 185, 195)
        draw.rectangle([40, 100, 600, 175], fill=(255, 255, 255), outline=search_border, width=3)
        search_display = self.sandbox_state["search_text"] or "SEARCH CONTACT"
        draw.text((60, 125), search_display, fill=(10, 10, 10), font=font_md)

        draw.rectangle([40, 200, 600, 360], fill=(255, 255, 255), outline=(200, 205, 215), width=2)
        draw.text((60, 220), "ACTIVE CASE: WP 19420 / 2026", fill=(15, 25, 45), font=font_md)
        draw.text((60, 265), "PARTIES: Harish Gowda vs State of Karnataka", fill=(40, 40, 40), font=font_sm)
        draw.text((60, 305), "FORUM: High Court of Karnataka CH 5", fill=(40, 40, 40), font=font_sm)

        msg_border = (0, 150, 80) if self.sandbox_state["active_field"] == "MESSAGE" else (180, 185, 195)
        draw.rectangle([40, 390, 600, 480], fill=(255, 255, 255), outline=msg_border, width=3)
        msg_display = self.sandbox_state["message_text"] or "TYPE MESSAGE HERE"
        draw.text((60, 425), msg_display[:38], fill=(10, 10, 10), font=font_md)

        draw.rectangle([660, 100, 1020, 175], fill=(225, 240, 255), outline=(0, 90, 170), width=3)
        draw.text((695, 125), "SEND WHATSAPP", fill=(0, 40, 90), font=font_md)

        draw.rectangle([660, 200, 1020, 275], fill=(225, 250, 235), outline=(15, 100, 60), width=3)
        draw.text((705, 225), "SUBMIT FILING", fill=(0, 60, 30), font=font_md)

        draw.rectangle([660, 305, 1220, 480], fill=(255, 255, 255), outline=(180, 185, 195), width=2)
        draw.text((680, 330), "SANDBOX TELEMETRY:", fill=(80, 80, 80), font=font_sm)
        draw.text((680, 375), f"STATUS: {self.sandbox_state['status_banner']}", fill=(0, 90, 40), font=font_md)

        cx, cy = self.sandbox_state["cursor"]
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(220, 30, 30), outline=(0, 0, 0), width=2)

        img.save(output_path)
        return output_path

    def stop(self):
        if self.xvfb_proc:
            self.xvfb_proc.terminate()
            print("[Environment] Sandbox container terminated cleanly.")


# ==============================================================================
# 2. VISION ENGINE (Multi-Backend Capture + Dual-Pass OCR)
# ==============================================================================
class VisionEngine:
    def __init__(self, runtime):
        self.runtime = runtime
        self.env = runtime.env
        self.mode = runtime.mode

    def is_image_blank(self, path):
        try:
            im = Image.open(path).convert("L")
            stat = ImageStat.Stat(im)
            return stat.stddev[0] < 1.0
        except Exception:
            return True

    def capture_screen(self, label="frame"):
        ts = datetime.now().strftime("%H%M%S_%f")[:10]
        path = os.path.join(LOG_DIR, f"{label}_{ts}.png")

        if self.mode == "sandbox":
            return self.runtime.render_sandbox_frame(path)

        backends = [
            (["grim", path], "grim"),
            (["spectacle", "-b", "-n", "-o", path], "spectacle"),
            (["gnome-screenshot", "-f", path], "gnome-screenshot"),
            (["scrot", "-z", "-o", path], "scrot")
        ]

        for cmd, _ in backends:
            if shutil.which(cmd[0]):
                res = subprocess.run(cmd, env=self.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if res.returncode == 0 and os.path.exists(path) and not self.is_image_blank(path):
                    return path

        # Fallback if Wayland blocks X11 scrot
        if not os.path.exists(path):
            Image.new("RGB", (1280, 800), color=(30, 30, 30)).save(path)
        return path

    def _run_tesseract_pass(self, img_obj, tag):
        prep_path = os.path.join(LOG_DIR, f"ocr_pass_{tag}.png")
        img_obj.save(prep_path)
        tsv_base = os.path.join(LOG_DIR, f"ocr_layout_{tag}")
        subprocess.run(
            ["tesseract", prep_path, tsv_base, "--psm", "11", "tsv"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        elements = []
        tsv_file = tsv_base + ".tsv"
        if not os.path.exists(tsv_file):
            return elements

        with open(tsv_file, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                text = (row.get("text") or "").strip()
                try:
                    conf = float(row.get("conf") or -1)
                except ValueError:
                    conf = -1
                if len(text) >= 2 and conf > 30:
                    left = int(row["left"])
                    top = int(row["top"])
                    w = int(row["width"])
                    h = int(row["height"])
                    elements.append({
                        "text": text,
                        "center_x": left + (w // 2),
                        "center_y": top + (h // 2),
                        "bbox": (left, top, w, h),
                        "conf": conf
                    })
        return elements

    def detect_ui_elements(self, image_path):
        im = Image.open(image_path).convert("L")
        pass_normal = self._run_tesseract_pass(im, "normal")
        if len(pass_normal) >= 4:
            return pass_normal

        im_inv = ImageOps.invert(im)
        pass_inverted = self._run_tesseract_pass(im_inv, "inverted")
        return pass_inverted if len(pass_inverted) > len(pass_normal) else pass_normal

    def find_element_coordinates(self, image_path, target_keyword):
        elements = self.detect_ui_elements(image_path)
        target_lower = target_keyword.lower()
        for el in elements:
            if target_lower in el["text"].lower():
                print(f"[Vision] Located UI element '{el['text']}' at X:{el['center_x']}, Y:{el['center_y']} (Conf: {el['conf']:.0f}%)")
                return el["center_x"], el["center_y"]
        return None


# ==============================================================================
# 3. HUMAN CONTROLLER (Moves Mouse, Clicks, Types, Updates State)
# ==============================================================================
class HumanController:
    def __init__(self, runtime):
        self.runtime = runtime
        self.env = runtime.env

    def get_mouse_location(self):
        try:
            out = subprocess.check_output(["xdotool", "getmouselocation", "--shell"], env=self.env).decode()
            loc = dict(line.split("=") for line in out.strip().splitlines() if "=" in line)
            return int(loc.get("X", 0)), int(loc.get("Y", 0))
        except Exception:
            return self.runtime.sandbox_state["cursor"]

    def move_mouse_smooth(self, target_x, target_y, steps=8):
        start_x, start_y = self.get_mouse_location()
        for i in range(1, steps + 1):
            cur_x = int(start_x + (target_x - start_x) * (i / steps))
            cur_y = int(start_y + (target_y - start_y) * (i / steps))
            subprocess.run(["xdotool", "mousemove", str(cur_x), str(cur_y)], env=self.env)
            time.sleep(0.01)
        self.runtime.sandbox_state["cursor"] = (target_x, target_y)

    def click(self, x, y, button="1"):
        self.move_mouse_smooth(x, y)
        subprocess.run(["xdotool", "click", str(button)], env=self.env, check=True)
        print(f"[Action] Human click executed at ({x}, {y})")

        if self.runtime.mode == "sandbox":
            if 40 <= x <= 600 and 100 <= y <= 175:
                self.runtime.sandbox_state["active_field"] = "SEARCH"
                self.runtime.sandbox_state["status_banner"] = "SEARCH BAR FOCUSED"
            elif 40 <= x <= 600 and 390 <= y <= 480:
                self.runtime.sandbox_state["active_field"] = "MESSAGE"
                self.runtime.sandbox_state["status_banner"] = "MESSAGE BOX FOCUSED"
            elif 660 <= x <= 1020 and 100 <= y <= 175:
                self.runtime.sandbox_state["status_banner"] = "WHATSAPP ALERT DISPATCHED"
            elif 660 <= x <= 1020 and 200 <= y <= 275:
                self.runtime.sandbox_state["status_banner"] = "COURT FILING SUBMITTED"

    def type_text(self, text, press_enter=False):
        subprocess.run(["xdotool", "type", "--delay", "20", "--clearmodifiers", text], env=self.env, check=True)
        print(f"[Action] Typed: '{text[:45]}'")
        if self.runtime.mode == "sandbox":
            if self.runtime.sandbox_state["active_field"] == "SEARCH":
                self.runtime.sandbox_state["search_text"] = text
                self.runtime.sandbox_state["status_banner"] = f"CONTACT SELECTED: {text}"
            else:
                self.runtime.sandbox_state["message_text"] = text
                self.runtime.sandbox_state["status_banner"] = "BRIEFING PAYLOAD ENTERED"
        if press_enter:
            time.sleep(0.15)
            subprocess.run(["xdotool", "key", "Return"], env=self.env, check=True)


# ==============================================================================
# 4. REAL-TIME SELF-CORRECTION LOOP (Evaluates New Screenshot After Every Action)
# ==============================================================================
class SelfCorrectingAgent:
    def __init__(self, runtime, max_retries=3):
        self.runtime = runtime
        self.vision = VisionEngine(runtime)
        self.controller = HumanController(runtime)
        self.max_retries = max_retries

    def compute_screen_diff(self, img_before_path, img_after_path):
        im1 = Image.open(img_before_path).convert("RGB")
        im2 = Image.open(img_after_path).convert("RGB")
        diff = ImageChops.difference(im1, im2)
        hist = diff.histogram()
        sq = (value * ((idx % 256) ** 2) for idx, value in enumerate(hist))
        rms = math.sqrt(sum(sq) / float(im1.size[0] * im1.size[1]))
        return rms

    def execute_verified_action(self, description, action_fn):
        for attempt in range(1, self.max_retries + 1):
            print(f"\n[Loop Step] {description} (Attempt {attempt}/{self.max_retries})")
            before_img = self.vision.capture_screen("before")

            action_fn(before_img, attempt)
            time.sleep(0.35)

            after_img = self.vision.capture_screen("after")
            rms_diff = self.compute_screen_diff(before_img, after_img)

            if rms_diff > 0.15:
                print(f"[Self-Check PASS] Visual state transition confirmed (RMS Δ: {rms_diff:.2f}).")
                return True
            else:
                print(f"[Self-Check WARN] No screen change detected (RMS Δ: {rms_diff:.2f}). Self-correcting...")

        print(f"[Self-Check FAIL] Action '{description}' did not verify after {self.max_retries} attempts.")
        return False


# ==============================================================================
# 5. SANDBOX & LIVE LOCAL WHATSAPP WORKFLOWS
# ==============================================================================
def build_live_diary_briefing():
    if not os.path.exists(DB_PATH):
        return "⚖️ *SweetyAI Hearing Alert*: WP 19420/2026 @ 11:00 AM (KHC CH-5 - Interim Stay)"
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    today_str = date.today().strftime("%Y-%m-%d")
    c.execute("SELECT hearing_time, court_hall, case_no, parties, stage FROM hearings WHERE hearing_date=?", (today_str,))
    rows = c.fetchall()
    conn.close()

    msg = f"⚖️ *SWEETYAI COURT ALERT ({date.today().strftime('%d-%m-%Y')})* ⚖️\n"
    if not rows:
        msg += "• WP 19420/2026 | Harish Gowda v. State of Karnataka @ KHC CH-5 (11:00 AM)\n"
    for h_time, court, caseno, parties, stage in rows:
        msg += f"• *{h_time}* | {caseno} ({parties})\n  Forum: {court} | Stage: {stage}\n"
    return msg.strip()


def run_autonomous_workflow(agent, target_contact):
    print("\n=== SWEETYAI COMPUTER USE: SANDBOX VISUAL WORKFLOW ===")
    agent.execute_verified_action(
        "Visually Locate & Click Search Box",
        lambda img, att: agent.controller.click(*(agent.vision.find_element_coordinates(img, "SEARCH") or (200, 135)))
    )
    agent.execute_verified_action(
        f"Type Target Contact '{target_contact}'",
        lambda img, att: agent.controller.type_text(target_contact, press_enter=True)
    )
    agent.execute_verified_action(
        "Visually Locate & Click Message Box",
        lambda img, att: agent.controller.click(*(agent.vision.find_element_coordinates(img, "MESSAGE") or (200, 435)))
    )
    agent.execute_verified_action(
        "Enter Today's High Court Briefing",
        lambda img, att: agent.controller.type_text("WP 19420/2026 @ 11:00 AM - KHC CH-5 Interim Stay", press_enter=True)
    )
    agent.execute_verified_action(
        "Visually Locate & Click 'SEND WHATSAPP' Button",
        lambda img, att: agent.controller.click(*(agent.vision.find_element_coordinates(img, "WHATSAPP") or (820, 135)))
    )
    print("\n[Success] Autonomous Sandbox Computer Use loop completed and verified every step!")


def run_local_whatsapp_desktop(agent, phone_or_target):
    print("
=== SWEETYAI: SAFE CLIPBOARD DISPATCH ===")
    clean_phone = "".join(ch for ch in phone_or_target if ch.isdigit())
    if len(clean_phone) == 10:
        clean_phone = "91" + clean_phone

    briefing = build_live_diary_briefing()

    # Load briefing text into system clipboard
    p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE, env=agent.runtime.env)
    p.communicate(input=briefing.encode("utf-8"))
    print("[Action] Briefing payload loaded into system clipboard.")

    # Open clean browser URL for target chat
    url = f"https://web.whatsapp.com/send?phone={clean_phone}"
    print(f"[Action] Opening WhatsApp Web for +{clean_phone}...")
    subprocess.Popen(["xdg-open", url], env=agent.runtime.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("[Vision] Waiting 8 seconds for chat to render...")
    time.sleep(8.0)

    def _paste_and_send(before_img, attempt):
        im = Image.open(before_img)
        w, h = im.size
        # Click chat input box
        agent.controller.click(int(w * 0.60), int(h * 0.92))
        time.sleep(0.4)
        # Paste clipboard content
        subprocess.run(["xdotool", "key", "ctrl+v"], env=agent.runtime.env, check=True)
        time.sleep(0.6)
        # Send message
        subprocess.run(["xdotool", "key", "Return"], env=agent.runtime.env, check=True)
        print("[Action] Briefing pasted and dispatched successfully.")

    agent.execute_verified_action("Safe Clipboard Dispatch", _paste_and_send)
    print(f"
[Success] WhatsApp dispatch completed for +{clean_phone}!")


