import json
import sqlite3
from pathlib import Path

MEMORY_FILE = Path(__file__).parent / "memory.json"
DB_FILE = Path(__file__).parent / "chat_history.db"


class Memory:

    def __init__(self):
        self.memories = []
        self.load()

    def load(self):

        if not MEMORY_FILE.exists():
            self.memories = []
            return

        try:
            with open(
                MEMORY_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                self.memories = json.load(file)

        except Exception:
            self.memories = []

    def save(self):

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.memories,
                file,
                indent=2,
                ensure_ascii=False
            )

    def add(self, memory):

        memory = memory.strip()

        if not memory:
            return "Memory was empty."

        if memory not in self.memories:

            self.memories.append(memory)
            self.save()

            return f"Memory saved: {memory}"

        return f"Memory already exists: {memory}"

    def delete(self, memory):

        memory = memory.strip()

        if memory in self.memories:

            self.memories.remove(memory)
            self.save()

            return f"Memory deleted: {memory}"

        return f"Memory not found: {memory}"

    def get_all(self):

        return self.memories

    def clear(self):

        self.memories = []
        self.save()

        return "All memories cleared."


# ==========================================
# SQLite Chat History Functions for SweetyAI
# ==========================================

def init_db():
    """Initializes the local SQLite chat history database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_message(role, content):
    """Saves a user or assistant message to the local database."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()

def get_recent_history(limit=6):
    """Retrieves recent conversation history in chronological order."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM messages ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    rows.reverse()
    history = []
    for role, content in rows:
        label = "User" if role == "user" else "SweetyAI"
        history.append(f"{label}: {content}")
    
    return "\n".join(history)