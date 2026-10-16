import os
import tempfile
import pytest

from app.adaptive.biometric_cadence import BiometricCadenceModel
from app.adaptive.persona_engine import PersonaEngine
from app.adaptive.dry_run_patcher import DryRunPatcher


def test_biometric_cadence_classification():
    model = BiometricCadenceModel()

    # Rapid flow typing: high WPM, low variance, low backspaces
    events_flow = []
    base_t = 1000.0
    for i in range(40):
        events_flow.append({"key": "a", "timestamp": base_t + (i * 90.0), "type": "keydown"})

    metrics_flow = model.analyze_keystroke_series(events_flow, duration_ms=3600.0)
    assert metrics_flow.cognitive_state in ("FOCUSED_FLOW", "URGENT_BURST")
    assert metrics_flow.wpm > 30.0

    # Hesitation / struggle typing: high backspaces, long pauses
    events_struggle = [
        {"key": "a", "timestamp": 1000.0, "type": "keydown"},
        {"key": "Backspace", "timestamp": 1200.0, "type": "keydown"},
        {"key": "b", "timestamp": 4500.0, "type": "keydown"},  # 3.3s pause
        {"key": "Backspace", "timestamp": 4700.0, "type": "keydown"},
        {"key": "c", "timestamp": 8000.0, "type": "keydown"},  # 3.3s pause
        {"key": "Backspace", "timestamp": 8200.0, "type": "keydown"},
    ]
    metrics_struggle = model.analyze_keystroke_series(events_struggle, duration_ms=8000.0)
    assert metrics_struggle.cognitive_state == "HESITATION_STRUGGLE"
    assert metrics_struggle.backspace_count == 3


def test_persona_engine_transitions():
    engine = PersonaEngine()
    assert engine.current_state.name == "neutral"

    # Transition to celebrating
    celebrate_state = engine.transition_to_celebrating("Contract review finished")
    assert celebrate_state.name == "celebrating"
    assert celebrate_state.avatar_emote == "proud"
    assert celebrate_state.glow_theme == "glow-celebrating"

    # Transition to alert
    alert_state = engine.transition_to_alert("Signature missing")
    assert alert_state.name == "alert"
    assert alert_state.avatar_emote == "alert"


def test_dry_run_patcher():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "app.py")
        orig_content = "def hello():\n    print('hi')\n"
        with open(test_file, "w") as f:
            f.write(orig_content)

        patcher = DryRunPatcher()

        # Preview patch
        new_content = "def hello():\n    print('hello world!')\n"
        preview = patcher.preview_patch(test_file, new_content)

        assert preview.lines_changed >= 1
        assert preview.checksum_before != preview.checksum_after
        assert "-    print('hi')" in preview.diff.unified_diff
        assert "+    print('hello world!')" in preview.diff.unified_diff

        # Apply patch
        res = patcher.apply_patch(test_file, new_content, create_backup=True)
        assert res["ok"] is True
        assert res["checkpoint_id"] is not None

        # Verify disk
        with open(test_file, "r") as f:
            content_on_disk = f.read()
        assert content_on_disk == new_content
