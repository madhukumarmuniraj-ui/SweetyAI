import time
import pytest

from app.background.scheduler import BackgroundScheduler
from app.background.notification_manager import NotificationManager, NotificationEvent
from app.background.case_watcher import CaseWatcher


def test_background_scheduler():
    scheduler = BackgroundScheduler()
    run_counter = {"count": 0}

    def sample_task():
        run_counter["count"] += 1
        return "success"

    task = scheduler.register_task("t1", "Counter Task", 0.5, sample_task)
    assert task.task_id == "t1"

    # Manual run
    res = scheduler.run_task_now("t1")
    assert res == "success"
    assert run_counter["count"] == 1

    # Start loop briefly
    scheduler.start()
    time.sleep(1.2)
    scheduler.stop()

    assert run_counter["count"] >= 2
    assert len(scheduler.list_tasks()) == 1


def test_notification_manager_broadcast_and_subscribe():
    notif_mgr = NotificationManager()
    sub_q = notif_mgr.subscribe()

    event = notif_mgr.broadcast(
        type="case_alert",
        title="High Court Listing",
        message="Item No. 12 before Bench 4",
        priority="HIGH",
        emote="proud",
    )

    assert event.title == "High Court Listing"
    assert not sub_q.empty()

    received_event = sub_q.get_nowait()
    assert received_event.id == event.id
    assert "High Court Listing" in received_event.to_sse()

    history = notif_mgr.get_history()
    assert len(history) >= 1
    assert history[0]["title"] == "High Court Listing"

    notif_mgr.unsubscribe(sub_q)


def test_case_watcher():
    notif_mgr = NotificationManager()
    scheduler = BackgroundScheduler()
    watcher = CaseWatcher(notification_mgr=notif_mgr, scheduler=scheduler)

    watch_item = watcher.add_watch(
        case_title="Acme Corp v Beta Industries",
        court="Delhi High Court",
        docket_number="ARB.P. 450/2026",
        keywords=["arbitration", "section 11"],
    )

    assert watch_item.docket_number == "ARB.P. 450/2026"
    assert len(watcher.list_watches()) == 1

    # Trigger status change
    update = watcher.trigger_status_update(
        watch_id=watch_item.watch_id,
        new_status="Arbitrator Appointed",
        summary="Justice (Retd.) Rao appointed as Sole Arbitrator.",
        next_hearing_date="2026-11-15",
    )

    assert update is not None
    assert update.previous_status == "Pending Admission"
    assert update.new_status == "Arbitrator Appointed"

    # Verify notification was broadcasted
    history = notif_mgr.get_history()
    assert len(history) >= 1
    assert "ARB.P. 450/2026" in history[0]["title"]
