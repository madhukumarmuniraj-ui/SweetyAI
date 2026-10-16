from __future__ import annotations

import logging
import sys
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class WindowContext:
    title: str
    process_name: str = "unknown"
    app_category: str = "other"  # "code_editor", "terminal", "document_viewer", "browser", "other"
    is_private: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": "[REDACTED - PRIVACY]" if self.is_private else self.title,
            "process_name": self.process_name,
            "app_category": self.app_category,
            "is_private": self.is_private,
            "timestamp": self.timestamp,
        }


class AmbientMonitor:
    """
    Monitors active foreground application window, context category,
    and enforces strict privacy filtering before context processing.
    """

    PRIVACY_DENYLIST: Set[str] = {
        "password", "bitwarden", "1password", "keepass", "lastpass",
        "banking", "netbanking", "login", "signin", "private browsing",
        "incognito", "authenticator", "keychain"
    }

    def __init__(self):
        self._last_context: Optional[WindowContext] = None
        self._lock = threading.RLock()

    def classify_app_category(self, title: str, process_name: str = "") -> str:
        text = f"{title} {process_name}".lower()

        if any(w in text for w in ["code", "visual studio", "cursor", "pycharm", "sublime", "neovim", "intellij"]):
            return "code_editor"
        if any(w in text for w in ["powershell", "cmd.exe", "terminal", "bash", "zsh", "iterm", "alacritty", "mintty"]):
            return "terminal"
        if any(w in text for w in ["pdf", "word", "winword", "docx", "acrobat", "reader", "notion", "obsidian"]):
            return "document_viewer"
        if any(w in text for w in ["chrome", "edge", "firefox", "brave", "safari", "opera"]):
            return "browser"
        if any(w in text for w in ["slack", "discord", "teams", "telegram", "whatsapp"]):
            return "chat"

        return "other"

    def is_private_window(self, title: str) -> bool:
        title_lower = title.lower()
        return any(term in title_lower for term in self.PRIVACY_DENYLIST)

    def get_active_window(self) -> WindowContext:
        """Retrieves active window context from OS with fallbacks."""
        title = "Desktop Workspace"
        process = "explorer.exe"

        if sys.platform == "win32":
            try:
                import pygetwindow as gw
                win = gw.getActiveWindow()
                if win and win.title:
                    title = win.title.strip()
            except Exception:
                pass

        is_priv = self.is_private_window(title)
        cat = self.classify_app_category(title, process)

        ctx = WindowContext(
            title=title,
            process_name=process,
            app_category=cat,
            is_private=is_priv,
        )

        with self._lock:
            self._last_context = ctx

        return ctx

    def evaluate_window(self, mock_title: str, mock_process: str = "") -> WindowContext:
        """Helper for testing and deterministic evaluation."""
        is_priv = self.is_private_window(mock_title)
        cat = self.classify_app_category(mock_title, mock_process)
        return WindowContext(
            title=mock_title,
            process_name=mock_process or "app.exe",
            app_category=cat,
            is_private=is_priv,
        )
