from __future__ import annotations

import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.ambient.ambient_monitor import WindowContext
from app.background.notification_manager import NotificationManager, get_notification_manager

logger = logging.getLogger(__name__)


@dataclass
class AnomalyAlert:
    category: str  # "RUNTIME_EXCEPTION", "SYNTAX_ERROR", "STATUTORY_GAP", "SECURITY_WARNING", "LOGICAL_INCONSISTENCY"
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    title: str
    description: str
    snippet: str
    suggested_action: str
    alert_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "category": self.category,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "snippet": self.snippet,
            "suggested_action": self.suggested_action,
            "timestamp": self.timestamp,
        }


class AnomalyDetector:
    """
    Real-time ambient anomaly and context inconsistency detector.
    Analyzes active editor/screen context for unhandled runtime exceptions,
    syntax errors, statutory citation ambiguities, and logical inconsistencies.
    """

    def __init__(self, notification_mgr: Optional[NotificationManager] = None):
        self.notification_mgr = notification_mgr or get_notification_manager()

    def detect_anomalies(
        self,
        text: str,
        window_ctx: Optional[WindowContext] = None,
        broadcast_alert: bool = True,
    ) -> List[AnomalyAlert]:
        alerts: List[AnomalyAlert] = []
        if not text or not text.strip():
            return alerts

        # 1. Check for Python/JS runtime exceptions
        if "Traceback (most recent call last):" in text or "Uncaught TypeError:" in text or "SyntaxError:" in text:
            exc_match = re.search(r"([A-Za-z0-9_]+Error:\s*[^\n]+)", text)
            exc_title = exc_match.group(1) if exc_match else "Runtime Exception Detected"
            alert = AnomalyAlert(
                category="RUNTIME_EXCEPTION",
                severity="HIGH",
                title=f"Ambient Anomaly: {exc_title}",
                description="Active terminal or editor session encountered an unhandled exception.",
                snippet=text[:300],
                suggested_action="Use SweetyAI Self-Healing Sandbox to auto-diagnose and repair the failing line.",
            )
            alerts.append(alert)

        # 2. Check for missing statutory references in legal context
        # e.g. "under Section 34 the award..." without specifying the Act
        ambiguous_section = re.search(r"(?i)\bSection\s+(\d+)\s+(?!of\s+the\s+[A-Za-z]+)(the\s+award|the\s+covenant|the\s+agreement)", text)
        if ambiguous_section:
            sec_num = ambiguous_section.group(1)
            alert = AnomalyAlert(
                category="STATUTORY_GAP",
                severity="MEDIUM",
                title=f"Statutory Ambiguity: Section {sec_num}",
                description=f"Drafting references Section {sec_num} without identifying the governing statutory Act.",
                snippet=ambiguous_section.group(0),
                suggested_action=f"Qualify citation (e.g., 'Section {sec_num} of the Arbitration and Conciliation Act, 1996').",
            )
            alerts.append(alert)

        # 3. Check for repealed IPC citation in modern 2024+ context
        if re.search(r"(?i)\bSection\s+(?:420|406|302)\s+(?:of\s+the\s+)?(?:IPC|Indian Penal Code)\b", text):
            alert = AnomalyAlert(
                category="STATUTORY_GAP",
                severity="HIGH",
                title="Repealed Statute: Indian Penal Code 1860",
                description="IPC has been repealed and replaced by Bharatiya Nyaya Sanhita, 2023 (effective 1 July 2024).",
                snippet=text[:200],
                suggested_action="Update citation to corresponding Bharatiya Nyaya Sanhita (BNS) 2023 section.",
            )
            alerts.append(alert)

        # 4. Check for Unmatched Parentheses or Brackets in Code
        if window_ctx and window_ctx.app_category == "code_editor":
            open_p = text.count("(")
            close_p = text.count(")")
            open_b = text.count("{")
            close_b = text.count("}")
            if abs(open_p - close_p) > 2 or abs(open_b - close_b) > 2:
                alert = AnomalyAlert(
                    category="SYNTAX_ERROR",
                    severity="MEDIUM",
                    title="Syntax Anomaly: Unmatched Enclosing Brackets",
                    description=f"Detected bracket imbalance (Parentheses: {open_p}/{close_p}, Braces: {open_b}/{close_b}).",
                    snippet=text[:150],
                    suggested_action="Verify closing brackets before running.",
                )
                alerts.append(alert)

        # Broadcast if requested
        if broadcast_alert and alerts:
            top_alert = alerts[0]
            if top_alert.severity in ("CRITICAL", "HIGH"):
                self.notification_mgr.broadcast(
                    type="anomaly_warning",
                    title=top_alert.title,
                    message=top_alert.description,
                    priority=top_alert.severity,
                    emote="alert",
                    data=top_alert.to_dict(),
                )

        return alerts
