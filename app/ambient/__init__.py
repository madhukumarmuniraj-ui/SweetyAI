"""
Ambient Intelligence and Real-Time Screen Context Subsystem for SweetyAI.
"""

from app.ambient.ambient_monitor import AmbientMonitor, WindowContext
from app.ambient.ocr_engine import OCREngine, TextBlock
from app.ambient.anomaly_detector import AnomalyDetector, AnomalyAlert
from app.ambient.context_prefetcher import ContextPrefetcher, StagedContextItem

__all__ = [
    "AmbientMonitor",
    "WindowContext",
    "OCREngine",
    "TextBlock",
    "AnomalyDetector",
    "AnomalyAlert",
    "ContextPrefetcher",
    "StagedContextItem",
]
