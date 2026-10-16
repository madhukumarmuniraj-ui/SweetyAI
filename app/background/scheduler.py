from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ScheduledTask:
    task_id: str
    name: str
    interval_seconds: float
    fn: Callable[[], Any]
    enabled: bool = True
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    run_count: int = 0
    last_error: Optional[str] = None
    last_result: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "interval_seconds": self.interval_seconds,
            "enabled": self.enabled,
            "last_run": self.last_run,
            "next_run": self.next_run,
            "run_count": self.run_count,
            "last_error": self.last_error,
        }


class BackgroundScheduler:
    """
    Thread-safe background daemon task scheduler executing periodic monitoring,
    legal docket updates, and system health sweeps.
    """

    def __init__(self):
        self._tasks: Dict[str, ScheduledTask] = {}
        self._lock = threading.RLock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def register_task(
        self,
        task_id: str,
        name: str,
        interval_seconds: float,
        fn: Callable[[], Any],
        enabled: bool = True,
    ) -> ScheduledTask:
        with self._lock:
            next_run = (datetime.now() + timedelta(seconds=interval_seconds)).isoformat()
            task = ScheduledTask(
                task_id=task_id,
                name=name,
                interval_seconds=max(1.0, float(interval_seconds)),
                fn=fn,
                enabled=enabled,
                next_run=next_run,
            )
            self._tasks[task_id] = task
            logger.info(f"[Scheduler] Registered task '{name}' (every {interval_seconds}s)")
            return task

    def unregister_task(self, task_id: str) -> bool:
        with self._lock:
            return self._tasks.pop(task_id, None) is not None

    def enable_task(self, task_id: str, enabled: bool = True) -> bool:
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.enabled = enabled
                return True
            return False

    def run_task_now(self, task_id: str) -> Optional[Any]:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return None

        try:
            res = task.fn()
            with self._lock:
                task.last_run = datetime.now().isoformat()
                task.run_count += 1
                task.last_result = res
                task.last_error = None
            return res
        except Exception as e:
            logger.error(f"[Scheduler] Task '{task.name}' failed: {e}")
            with self._lock:
                task.last_run = datetime.now().isoformat()
                task.last_error = str(e)
            return None

    def list_tasks(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [t.to_dict() for t in self._tasks.values()]

    def start(self) -> None:
        with self._lock:
            if self._running:
                return
            self._running = True
            self._thread = threading.Thread(target=self._loop, daemon=True, name="SweetyScheduler")
            self._thread.start()
            logger.info("[Scheduler] Background scheduler loop started.")

    def stop(self) -> None:
        with self._lock:
            self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        logger.info("[Scheduler] Background scheduler loop stopped.")

    def _loop(self) -> None:
        while self._running:
            now = datetime.now()
            tasks_to_run = []

            with self._lock:
                for task in self._tasks.values():
                    if not task.enabled:
                        continue
                    if task.next_run is None or now >= datetime.fromisoformat(task.next_run):
                        tasks_to_run.append(task)
                        task.next_run = (now + timedelta(seconds=task.interval_seconds)).isoformat()

            for task in tasks_to_run:
                try:
                    res = task.fn()
                    with self._lock:
                        task.last_run = datetime.now().isoformat()
                        task.run_count += 1
                        task.last_result = res
                        task.last_error = None
                except Exception as e:
                    logger.error(f"[Scheduler] Periodic task '{task.name}' error: {e}")
                    with self._lock:
                        task.last_run = datetime.now().isoformat()
                        task.last_error = str(e)

            time.sleep(0.5)


_GLOBAL_SCHEDULER: Optional[BackgroundScheduler] = None


def get_background_scheduler() -> BackgroundScheduler:
    global _GLOBAL_SCHEDULER
    if _GLOBAL_SCHEDULER is None:
        _GLOBAL_SCHEDULER = BackgroundScheduler()
        _GLOBAL_SCHEDULER.start()
    return _GLOBAL_SCHEDULER
