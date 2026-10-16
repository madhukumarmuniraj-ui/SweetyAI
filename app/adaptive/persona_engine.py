from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.adaptive.biometric_cadence import CadenceMetrics
from app.background.notification_manager import NotificationManager, get_notification_manager

logger = logging.getLogger(__name__)


@dataclass
class PersonaState:
    name: str  # "focused", "hesitant", "celebrating", "alert", "neutral"
    glow_theme: str  # "glow-focused", "glow-hesitant", "glow-celebrating", "glow-alert", "glow-neutral"
    fire_ring_colors: List[str]
    avatar_emote: str = "idle"
    audio_cue: str = "none"
    suppress_non_critical: bool = False
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "glow_theme": self.glow_theme,
            "fire_ring_colors": self.fire_ring_colors,
            "avatar_emote": self.avatar_emote,
            "audio_cue": self.audio_cue,
            "suppress_non_critical": self.suppress_non_critical,
            "reason": self.reason,
        }


class PersonaEngine:
    """
    Coordinates emotional, biometric, and UI sensory feedback across
    Dynamic Island avatar emotes, fire-ring shaders, and audio cues.
    """

    def __init__(self, notification_mgr: Optional[NotificationManager] = None):
        self.notification_mgr = notification_mgr or get_notification_manager()
        self.current_state: PersonaState = self._create_neutral_state()

    def _create_neutral_state(self) -> PersonaState:
        return PersonaState(
            name="neutral",
            glow_theme="glow-neutral",
            fire_ring_colors=["#2979ff", "#00e5ff"],
            avatar_emote="idle",
            audio_cue="none",
            suppress_non_critical=False,
            reason="Standard balanced state",
        )

    def transition_from_cadence(self, cadence: CadenceMetrics) -> PersonaState:
        cog = cadence.cognitive_state

        if cog == "FOCUSED_FLOW":
            new_state = PersonaState(
                name="focused",
                glow_theme="glow-focused",
                fire_ring_colors=["#00e5ff", "#7c4dff"],
                avatar_emote="thinking",
                audio_cue="none",
                suppress_non_critical=True,
                reason="Focused flow state detected; suppressing non-critical interruptions.",
            )
        elif cog == "HESITATION_STRUGGLE":
            new_state = PersonaState(
                name="hesitant",
                glow_theme="glow-hesitant",
                fire_ring_colors=["#ffb300", "#ff6d00"],
                avatar_emote="greet",
                audio_cue="chime",
                suppress_non_critical=False,
                reason="High correction/hesitation detected; offering encouraging assistance.",
            )
        elif cog == "URGENT_BURST":
            new_state = PersonaState(
                name="focused",
                glow_theme="glow-focused",
                fire_ring_colors=["#00e676", "#00e5ff"],
                avatar_emote="thinking",
                audio_cue="none",
                suppress_non_critical=True,
                reason="High-speed burst typing active.",
            )
        else:
            new_state = self._create_neutral_state()

        self.current_state = new_state
        return new_state

    def transition_to_celebrating(self, reason: str = "Task completed successfully!") -> PersonaState:
        new_state = PersonaState(
            name="celebrating",
            glow_theme="glow-celebrating",
            fire_ring_colors=["#ffd700", "#ff007f", "#00ffcc"],
            avatar_emote="proud",
            audio_cue="finish",
            suppress_non_critical=False,
            reason=reason,
        )
        self.current_state = new_state
        self.notification_mgr.broadcast(
            type="cadence_shift",
            title="Task Victory!",
            message=reason,
            priority="NORMAL",
            emote="proud",
            data=new_state.to_dict(),
        )
        return new_state

    def transition_to_alert(self, reason: str = "User approval required") -> PersonaState:
        new_state = PersonaState(
            name="alert",
            glow_theme="glow-alert",
            fire_ring_colors=["#ff1744", "#d50000"],
            avatar_emote="alert",
            audio_cue="approval",
            suppress_non_critical=False,
            reason=reason,
        )
        self.current_state = new_state
        return new_state
