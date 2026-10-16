from __future__ import annotations

import json
import logging
import queue
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class NotificationEvent:
    type: str  # "case_alert", "docket_update", "anomaly_warning", "system_status", "cadence_shift"
    title: str
    message: str
    priority: str = "NORMAL"  # "CRITICAL", "HIGH", "NORMAL", "LOW"
    emote: Optional[str] = None  # "proud", "greet", "surprised", "alert", "thinking"
    data: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "message": self.message,
            "priority": self.priority,
            "emote": self.emote,
            "data": self.data,
            "timestamp": self.timestamp,
        }

    def to_sse(self) -> str:
        payload = json.dumps(self.to_dict(), ensure_ascii=False)
        return f"event: {self.type}\ndata: {payload}\n\n"


class NotificationManager:
    """
    Priority notification hub and Server-Sent Events (SSE) dispatcher for SweetyAI.
    Dispatches real-time alerts to the floating Dynamic Island avatar and companion card.
    """

    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self._history: List[NotificationEvent] = []
        self._subscribers: Set[queue.Queue] = set()
        self._lock = threading.RLock()

    def subscribe(self) -> queue.Queue:
        q: queue.Queue = queue.Queue(maxsize=100)
        with self._lock:
            self._subscribers.add(q)
            logger.info(f"[NotificationManager] New SSE subscriber connected. Total: {len(self._subscribers)}")
        return q

    def unsubscribe(self, q: queue.Queue) -> None:
        with self._lock:
            self._subscribers.discard(q)
            logger.info(f"[NotificationManager] Subscriber disconnected. Remaining: {len(self._subscribers)}")

    def register_listener(self) -> queue.Queue:
        return self.subscribe()

    def unregister_listener(self, q: queue.Queue) -> None:
        self.unsubscribe(q)

    def broadcast(
        self,
        type: str,
        title: str,
        message: str,
        priority: str = "NORMAL",
        emote: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> NotificationEvent:
        event = NotificationEvent(
            type=type,
            title=title,
            message=message,
            priority=priority,
            emote=emote,
            data=data or {},
        )
        with self._lock:
            self._history.append(event)
            if len(self._history) > self.max_history:
                self._history.pop(0)

            dead_queues = []
            for q in list(self._subscribers):
                try:
                    q.put_nowait(event)
                except queue.Full:
                    dead_queues.append(q)

            for dq in dead_queues:
                self._subscribers.discard(dq)

        logger.info(f"[NotificationManager] Broadcasted alert: [{priority}] {title}")
        return event

    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._lock:
            return [e.to_dict() for e in reversed(self._history[-limit:])]

    def clear_history(self) -> None:
        with self._lock:
            self._history.clear()


_GLOBAL_NOTIFICATION_MGR: Optional[NotificationManager] = None


def get_notification_manager() -> NotificationManager:
    global _GLOBAL_NOTIFICATION_MGR
    if _GLOBAL_NOTIFICATION_MGR is None:
        _GLOBAL_NOTIFICATION_MGR = NotificationManager()
    return _GLOBAL_NOTIFICATION_MGR
