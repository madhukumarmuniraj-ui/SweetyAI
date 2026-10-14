import os
import re
import time
import shutil
import subprocess
import urllib.request
from html.parser import HTMLParser


class LayoutAndNetworkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.has_viewport = False
        self.has_charset = False
        self.has_title = False
        self.blocking_scripts = []
        self.images_missing_alt = []
        self.fixed_width_elements = []
        self.assets = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == "meta":
            if attr_dict.get("name", "").lower() == "viewport":
                self.has_viewport = True
            if "charset" in attr_dict:
                self.has_charset = True
        elif tag == "title":
            self.has_title = True
        elif tag == "script":
            src = attr_dict.get("src")
            if src:
                self.assets.append(("script", src))
                if "defer" not in attr_dict and "async" not in attr_dict and attr_dict.get("type") != "module":
                    self.blocking_scripts.append(src)
        elif tag == "link":
            href = attr_dict.get("href")
            if href:
                self.assets.append(("style", href))
        elif tag == "img":
            src = attr_dict.get("src", "<inline-img>")
            self.assets.append(("image", src))
            if "alt" not in attr_dict:
                self.images_missing_alt.append(src)

        style = attr_dict.get("style", "")
        if "width:" in style:
            match = re.search(r"width\s*:\s*(\d+)px", style)
            if match and int(match.group(1)) > 1200:
                self.fixed_width_elements.append((tag, match.group(0)))


def find_headless_browser():
    for binary in ["google-chrome", "chromium", "chromium-browser", "brave-browser"]:
        path = shutil.which(binary)
        if path:
            return path
    return None


def inspect_network(url):
    report = {
        "status": None,
        "latency_ms": None,
        "payload_bytes": 0,
        "constraints": [],
        "html": "",
    }
    start = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SweetyAI-Headless-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()
            elapsed = round((time.time() - start) * 1000, 2)
            report["status"] = resp.status
            report["latency_ms"] = elapsed
            report["payload_bytes"] = len(content)
            report["html"] = content.decode("utf-8", errors="replace")
            if elapsed > 500:
                report["constraints"].append(f"High TTFB/Network Latency: {elapsed}ms (>500ms threshold)")
            if len(content) > 500_000:
                report["constraints"].append(f"Heavy HTML Payload: {len(content) // 1024}KB")
    except Exception as e:
        report["constraints"].append(f"Network Connection Failed: {e}")
    return report


def run_headless_dom_dump(target):
    browser = find_headless_browser()
    if not browser:
        return None, "Built-in DOM/Network Inspector (No local Chrome binary needed)"
    try:
        cmd = [browser, "--headless", "--disable-gpu", "--no-sandbox", "--dump-dom", target]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout, f"Rendered DOM via Headless Chrome ({os.path.basename(browser)})"
        return None, f"Headless Chrome exited with code {proc.returncode}"
    except Exception as e:
        return None, f"Headless Chrome note: {e}"


def audit_and_patch(target, auto_patch=False):
    print("\n=== SweetyAI Headless DevTools & Auto-Patch Agent ===")
    print(f"Target       : {target}")
    print(f"Auto-Patch   : {'ENABLED' if auto_patch else 'DISABLED (Audit Only)'}")

    is_local_file = os.path.exists(target)
    html_content = ""

    if target.startswith("http://") or target.startswith("https://"):
        net_report = inspect_network(target)
        print(f"\n[1] Network Constraints & Telemetry:")
        print(f"  - HTTP Status  : {net_report['status']}")
        print(f"  - Latency      : {net_report['latency_ms']} ms")
        print(f"  - Payload Size : {net_report['payload_bytes']} bytes")
        if net_report["constraints"]:
            for c in net_report["constraints"]:
                print(f"  - [!] Constraint: {c}")
        else:
            print("  - Network Status: Healthy (Low latency, optimal payload)")
        html_content = net_report["html"]
    elif is_local_file:
        with open(target, "r", encoding="utf-8", errors="replace") as f:
            html_content = f.read()
        print(f"\n[1] Local Target & Network Telemetry:")
        print(f"  - File Size    : {len(html_content)} bytes")
        net_report = inspect_network("http://127.0.0.1:8765/")
        if net_report["status"]:
            print(f"  - Local Daemon : Online ({net_report['latency_ms']} ms response on 127.0.0.1:8765)")
    else:
        print(f"[Error] Target '{target}' not found.")
        return

    target_uri = f"file://{os.path.abspath(target)}" if is_local_file else target
    rendered_dom, browser_msg = run_headless_dom_dump(target_uri)
    print(f"\n[2] Headless Browser Engine:")
    print(f"  - Engine       : {browser_msg}")
    dom_to_parse = rendered_dom if rendered_dom else html_content

    parser = LayoutAndNetworkParser()
    parser.feed(dom_to_parse)

    flaws = []
    if not parser.has_viewport:
        flaws.append("missing_viewport: Missing responsive <meta name='viewport'> tag.")
    if not parser.has_charset:
        flaws.append("missing_charset: Missing <meta charset='UTF-8'> declaration.")
    if parser.blocking_scripts:
        flaws.append(f"render_blocking_scripts: {len(parser.blocking_scripts)} synchronous <script> tag(s): {', '.join(parser.blocking_scripts)}")
    if parser.images_missing_alt:
        flaws.append(f"missing_alt: {len(parser.images_missing_alt)} <img> element(s) missing alt attributes.")
    if parser.fixed_width_elements:
        flaws.append(f"horizontal_overflow: Elements with rigid pixel widths >1200px: {parser.fixed_width_elements}")

    if is_local_file:
        base_dir = os.path.dirname(os.path.abspath(target))
        for asset_type, asset_path in parser.assets:
            if not asset_path.startswith(("http://", "https://", "data:", "//")):
                clean_path = asset_path.split("?")[0].lstrip("/")
                full_asset = os.path.join(base_dir, clean_path)
                if not os.path.exists(full_asset):
                    flaws.append(f"broken_asset: Missing linked {asset_type} file '{asset_path}'")

    print(f"\n[3] Layout & DOM Diagnostic Report:")
    if not flaws:
        print("  - [OK] Zero layout or network-blocking flaws detected!")
    else:
        for idx, flaw in enumerate(flaws, 1):
            print(f"  - Flaw #{idx}: {flaw}")

    if auto_patch and is_local_file and flaws:
        print(f"\n[4] Autonomous Code Patcher:")
        backup_path = f"{target}.bak"
        shutil.copyfile(target, backup_path)
        patched_html = html_content
        patches_applied = []

        if not parser.has_viewport and "<head>" in patched_html:
            patched_html = patched_html.replace(
                "<head>",
                '<head>\n  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
                1,
            )
            patches_applied.append("Injected responsive <meta name='viewport'> into <head>")

        if not parser.has_charset and "<head>" in patched_html:
            patched_html = patched_html.replace(
                "<head>",
                '<head>\n  <meta charset="UTF-8">',
                1,
            )
            patches_applied.append("Injected <meta charset='UTF-8'> into <head>")

        if parser.images_missing_alt:
            patched_html, count = re.subn(
                r"<img(?![^>]*\balt=)([^>]*)>",
                r'<img alt="SweetyAI UI Asset"\1>',
                patched_html,
            )
            if count > 0:
                patches_applied.append(f"Patched {count} <img> tag(s) with missing alt attributes")

        if patches_applied:
            with open(target, "w", encoding="utf-8") as f:
                f.write(patched_html)
            print(f"  - Backup saved to: {backup_path}")
            for p in patches_applied:
                print(f"  - [PATCHED] {p}")
            print(f"  - Successfully patched '{target}' autonomously!")
        else:
            print("  - Diagnostics logged; no structural HTML mutations required.")
    print("=====================================================\n")
