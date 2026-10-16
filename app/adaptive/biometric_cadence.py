from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class CadenceMetrics:
    wpm: float
    avg_flight_time_ms: float
    flight_time_variance: float
    backspace_count: int
    total_keystrokes: int
    pause_count: int
    backspace_ratio: float
    cognitive_state: str  # "FOCUSED_FLOW", "HESITATION_STRUGGLE", "URGENT_BURST", "IDLE_FATIGUE", "BALANCED"
    confidence: float = 0.85
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "wpm": round(self.wpm, 1),
            "avg_flight_time_ms": round(self.avg_flight_time_ms, 1),
            "flight_time_variance": round(self.flight_time_variance, 1),
            "backspace_count": self.backspace_count,
            "total_keystrokes": self.total_keystrokes,
            "pause_count": self.pause_count,
            "backspace_ratio": round(self.backspace_ratio, 3),
            "cognitive_state": self.cognitive_state,
            "confidence": round(self.confidence, 2),
            "timestamp": self.timestamp,
        }


class BiometricCadenceModel:
    """
    Analyzes typing rhythm, inter-key flight times, correction frequencies,
    and pause intervals to infer cognitive load and flow states.
    """

    def analyze_keystroke_series(
        self,
        events: List[Dict[str, Any]],
        duration_ms: Optional[float] = None,
    ) -> CadenceMetrics:
        if not events or len(events) < 3:
            return CadenceMetrics(
                wpm=0.0,
                avg_flight_time_ms=0.0,
                flight_time_variance=0.0,
                backspace_count=0,
                total_keystrokes=len(events),
                pause_count=0,
                backspace_ratio=0.0,
                cognitive_state="BALANCED",
                confidence=0.5,
            )

        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda x: x.get("timestamp", 0))

        intervals: List[float] = []
        backspaces = 0
        pauses = 0

        for i in range(1, len(sorted_events)):
            t1 = float(sorted_events[i - 1].get("timestamp", 0))
            t2 = float(sorted_events[i].get("timestamp", 0))
            dt = max(0.0, t2 - t1)
            intervals.append(dt)

            if dt > 2500.0:  # Pause > 2.5s
                pauses += 1

            key = str(sorted_events[i].get("key", ""))
            if key.lower() in ("backspace", "delete", "ctrl+z"):
                backspaces += 1

        total_keys = len(sorted_events)
        backspace_ratio = backspaces / max(1, total_keys)

        avg_flight_time = sum(intervals) / max(1, len(intervals))

        # Variance calculation
        variance = sum((x - avg_flight_time) ** 2 for x in intervals) / max(1, len(intervals))

        # Calculate WPM
        calc_duration_ms = duration_ms or (sorted_events[-1]["timestamp"] - sorted_events[0]["timestamp"])
        duration_minutes = max(0.01, calc_duration_ms / 60000.0)
        # Standard: 5 characters per word
        wpm = (total_keys / 5.0) / duration_minutes

        # State classification
        if wpm > 75.0 and avg_flight_time < 130.0:
            state = "URGENT_BURST"
        elif backspace_ratio > 0.18 or pauses >= 3 or variance > 50000.0:
            state = "HESITATION_STRUGGLE"
        elif wpm >= 35.0 and backspace_ratio <= 0.12 and pauses <= 1:
            state = "FOCUSED_FLOW"
        elif avg_flight_time > 1000.0 or wpm < 15.0:
            state = "IDLE_FATIGUE"
        else:
            state = "BALANCED"

        return CadenceMetrics(
            wpm=wpm,
            avg_flight_time_ms=avg_flight_time,
            flight_time_variance=variance,
            backspace_count=backspaces,
            total_keystrokes=total_keys,
            pause_count=pauses,
            backspace_ratio=backspace_ratio,
            cognitive_state=state,
            confidence=0.85,
        )
