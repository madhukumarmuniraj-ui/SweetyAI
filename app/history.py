import json

HISTORY_FILE = "chat_history.json"
MAX_HISTORY_ITEMS = 50


def append_to_history(role, text):
    try:
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []
        history.append({"role": role, "content": text})
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history[-MAX_HISTORY_ITEMS:], f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get_history_string():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
        return "\n".join(
            f"{item['role']}: {item['content']}" for item in history[-10:]
        )
    except Exception:
        return ""
