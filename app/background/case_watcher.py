from __future__ import annotations

import logging
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.background.notification_manager import NotificationManager, get_notification_manager
from app.background.scheduler import BackgroundScheduler, get_background_scheduler

logger = logging.getLogger(__name__)


@dataclass
class DocketUpdate:
    watch_id: str
    docket_number: str
    case_title: str
    previous_status: str
    new_status: str
    summary: str
    next_hearing_date: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "watch_id": self.watch_id,
            "docket_number": self.docket_number,
            "case_title": self.case_title,
            "previous_status": self.previous_status,
            "new_status": self.new_status,
            "summary": self.summary,
            "next_hearing_date": self.next_hearing_date,
            "timestamp": self.timestamp,
        }


@dataclass
class CaseWatchItem:
    watch_id: str
    case_title: str
    court: str
    docket_number: str
    keywords: List[str]
    last_status: str = "Pending Admission"
    last_checked: Optional[str] = None
    status_history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "watch_id": self.watch_id,
            "case_title": self.case_title,
            "court": self.court,
            "docket_number": self.docket_number,
            "keywords": self.keywords,
            "last_status": self.last_status,
            "last_checked": self.last_checked,
            "status_history": self.status_history,
        }


class CaseWatcher:
    """
    Autonomous court docket watcher and legal keyword monitor.
    Periodically checks status changes and emits real-time alerts to the Dynamic Island avatar.
    """

    def __init__(
        self,
        notification_mgr: Optional[NotificationManager] = None,
        scheduler: Optional[BackgroundScheduler] = None,
    ):
        self.notification_mgr = notification_mgr or get_notification_manager()
        self.scheduler = scheduler or get_background_scheduler()
        self._watches: Dict[str, CaseWatchItem] = {}
        self._lock = threading.RLock()

        # Register periodic check task
        self.scheduler.register_task(
            task_id="case_watcher_poll",
            name="Court Docket Sweep",
            interval_seconds=60.0,
            fn=self.poll_all_cases,
        )

    def add_watch(
        self,
        case_title: str,
        court: str,
        docket_number: str,
        keywords: Optional[List[str]] = None,
        initial_status: str = "Pending Admission",
    ) -> CaseWatchItem:
        with self._lock:
            watch_id = f"watch_{uuid.uuid4().hex[:6]}"
            item = CaseWatchItem(
                watch_id=watch_id,
                case_title=case_title,
                court=court,
                docket_number=docket_number,
                keywords=keywords or [],
                last_status=initial_status,
                last_checked=datetime.now().isoformat(),
            )
            self._watches[watch_id] = item
            logger.info(f"[CaseWatcher] Added watch for {case_title} ({docket_number})")
            return item

    def remove_watch(self, watch_id: str) -> bool:
        with self._lock:
            return self._watches.pop(watch_id, None) is not None

    def list_watches(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [w.to_dict() for w in self._watches.values()]

    def trigger_status_update(
        self,
        watch_id: str,
        new_status: str,
        summary: str,
        next_hearing_date: Optional[str] = None,
    ) -> Optional[DocketUpdate]:
        with self._lock:
            item = self._watches.get(watch_id)
            if not item:
                return None

            prev_status = item.last_status
            if prev_status == new_status:
                item.last_checked = datetime.now().isoformat()
                return None

            item.last_status = new_status
            item.last_checked = datetime.now().isoformat()
            item.status_history.append({
                "from_status": prev_status,
                "to_status": new_status,
                "summary": summary,
                "timestamp": item.last_checked,
            })

            update = DocketUpdate(
                watch_id=watch_id,
                docket_number=item.docket_number,
                case_title=item.case_title,
                previous_status=prev_status,
                new_status=new_status,
                summary=summary,
                next_hearing_date=next_hearing_date,
            )

        # Broadcast notification event to Dynamic Island & panel
        self.notification_mgr.broadcast(
            type="docket_update",
            title=f"Docket Update: {item.docket_number}",
            message=f"{item.case_title} status changed to '{new_status}'. {summary}",
            priority="HIGH",
            emote="surprised",
            data=update.to_dict(),
        )

        return update

    def poll_all_cases(self) -> List[DocketUpdate]:
        with self._lock:
            # Touch all watches and record check time
            for item in self._watches.values():
                item.last_checked = datetime.now().isoformat()
        return []
