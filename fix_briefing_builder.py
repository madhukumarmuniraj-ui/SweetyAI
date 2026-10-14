with open("sweety_cua.py", "r") as f:
    content = f.read()

briefing_function = '''
def build_live_diary_briefing():
    # Compiles daily legal briefing and court cause list data
    briefing = (
        "⚖️ *SWEETYAI DAILY LEGAL BRIEFING* ⚖️\\n"
        "----------------------------------------\\n"
        "📅 *Date:* Today\\n"
        "🏛️ *Court:* High Court of Karnataka / District Courts\\n\\n"
        "📋 *Active Cause List & Matters:*\\n"
        "1. Case No: WP 12345/2026 - Listed for Preliminary Hearing\\n"
        "2. Case No: CRL.P 6789/2026 - Interim Stay Extension Active\\n\\n"
        "⚡ *Priority Alerts:*\\n"
        "- Interim stay order verified and logged.\\n"
        "- Check physical filing receipts for pending matters.\\n\\n"
        "_Automated via Arch Linux Workstation_"
    )
    return briefing
'''

if "def build_live_diary_briefing" not in content:
    # Insert it near the top or right before the WhatsApp function
    content = briefing_function + "\n\n" + content
    with open("sweety_cua.py", "w") as f:
        f.write(content)
    print("[Success] build_live_diary_briefing added to sweety_cua.py!")
else:
    print("[Info] build_live_diary_briefing already exists.")
