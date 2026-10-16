"""
Autonomous Background Research and Case Watchers Subsystem for SweetyAI.
"""

from app.background.scheduler import BackgroundScheduler, ScheduledTask
from app.background.case_watcher import CaseWatcher, CaseWatchItem, DocketUpdate
from app.background.notification_manager import (
    NotificationManager,
    NotificationEvent,
    get_notification_manager,
)

__all__ = [
    "BackgroundScheduler",
    "ScheduledTask",
    "CaseWatcher",
    "CaseWatchItem",
    "DocketUpdate",
    "NotificationManager",
    "NotificationEvent",
    "get_notification_manager",
]
