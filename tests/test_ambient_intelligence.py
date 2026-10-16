import pytest

from app.ambient.ambient_monitor import AmbientMonitor, WindowContext
from app.ambient.ocr_engine import OCREngine
from app.ambient.anomaly_detector import AnomalyDetector
from app.ambient.context_prefetcher import ContextPrefetcher
from app.background.notification_manager import NotificationManager


def test_ambient_monitor_privacy_and_classification():
    monitor = AmbientMonitor()

    # Code editor
    ctx1 = monitor.evaluate_window("main.py - SweetyAI - Visual Studio Code", "Code.exe")
    assert ctx1.app_category == "code_editor"
    assert ctx1.is_private is False

    # Document viewer
    ctx2 = monitor.evaluate_window("Commercial_Contract_Agreement.pdf - Adobe Acrobat Reader", "AcroRd32.exe")
    assert ctx2.app_category == "document_viewer"

    # Privacy filter on password manager
    ctx3 = monitor.evaluate_window("Bitwarden Password Vault - Google Chrome", "chrome.exe")
    assert ctx3.is_private is True
    assert ctx3.to_dict()["title"] == "[REDACTED - PRIVACY]"


def test_ocr_engine_snippet_classification():
    ocr = OCREngine()

    code_snippet = "def calculate_damages(contract_val, multiplier=2):\n    return contract_val * multiplier"
    blocks = ocr.extract_from_text_snippet(code_snippet)
    assert len(blocks) >= 1
    assert blocks[0].block_type == "code"

    error_snippet = "Traceback (most recent call last):\n  File 'app.py', line 12, in <module>\nZeroDivisionError: division by zero"
    blocks_err = ocr.extract_from_text_snippet(error_snippet)
    assert len(blocks_err) >= 1
    assert blocks_err[0].block_type == "error_trace"


def test_anomaly_detector():
    notif_mgr = NotificationManager()
    detector = AnomalyDetector(notification_mgr=notif_mgr)

    # Runtime exception detection
    err_text = "Traceback (most recent call last):\n  File 'server.py', line 45\nIndexError: list index out of range"
    alerts = detector.detect_anomalies(err_text, broadcast_alert=True)
    assert len(alerts) >= 1
    assert alerts[0].category == "RUNTIME_EXCEPTION"
    assert "IndexError" in alerts[0].title

    # Repealed IPC detection
    ipc_text = "The respondent is charged under Section 420 of the IPC for cheating."
    alerts_ipc = detector.detect_anomalies(ipc_text, broadcast_alert=False)
    assert len(alerts_ipc) >= 1
    assert alerts_ipc[0].category == "STATUTORY_GAP"
    assert "Bharatiya Nyaya Sanhita" in alerts_ipc[0].description


def test_context_prefetcher():
    notif_mgr = NotificationManager()
    detector = AnomalyDetector(notification_mgr=notif_mgr)
    prefetcher = ContextPrefetcher(anomaly_detector=detector)

    sample_context = "The petition is filed under Section 34 of the Arbitration and Conciliation Act challenging the award."
    staged = prefetcher.stage_from_context(sample_context)

    assert len(staged) >= 1
    queue = prefetcher.get_staged_queue()
    assert len(queue) >= 1
    assert any("Arbitration" in item["summary"] or "Arbitration" in item["title"] for item in queue)
