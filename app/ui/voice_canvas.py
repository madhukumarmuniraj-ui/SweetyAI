"""
SweetyAI - Real-Time Voice Streaming, Interactive Canvas & Proactive Notifications
Low-latency voice, dynamic UI generation, background monitoring, push notifications
"""

import os
import json
import time
import asyncio
import threading
import queue
from typing import Dict, Any, Optional, List, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid

# Audio / Voice
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False


# =============================================================================
# REAL-TIME VOICE STREAMING
# =============================================================================

class VoiceStreamState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    INTERRUPTED = "interrupted"


class VoiceStreamEngine:
    """Low-latency voice streaming with natural interruptions."""

    VOICES = {
        "default": "en-US-AriaNeural",
        "male": "en-US-GuyNeural",
        "female": "en-US-JennyNeural",
        "british": "en-GB-SoniaNeural",
        "indian": "en-IN-NeerjaNeural",
    }

    def __init__(self, voice: str = "default"):
        self.voice = self.VOICES.get(voice, voice)
        self.state = VoiceStreamState.IDLE
        self.recognizer = sr.Recognizer() if SR_AVAILABLE else None
        self._interrupt_flag = threading.Event()
        self._audio_queue: queue.Queue = queue.Queue()
        self._tts_thread: Optional[threading.Thread] = None
        self._listen_thread: Optional[threading.Thread] = None
        self.on_speech_detected: Optional[Callable[[str], None]] = None
        self.on_state_change: Optional[Callable[[VoiceStreamState], None]] = None
        self.lock = threading.Lock()

    def _set_state(self, new_state: VoiceStreamState):
        self.state = new_state
        if self.on_state_change:
            self.on_state_change(new_state)

    # ---- TTS ----

    def speak(self, text: str, interrupt_current: bool = True):
        """Speak text with edge-tts. Runs in background thread."""
        if not EDGE_TTS_AVAILABLE:
            print(f"[TTS] {text}")
            return

        if interrupt_current:
            self.stop_speaking()

        self._tts_thread = threading.Thread(target=self._speak_sync, args=(text,), daemon=True)
        self._tts_thread.start()

    def _speak_sync(self, text: str):
        self._set_state(VoiceStreamState.SPEAKING)
        self._interrupt_flag.clear()

        try:
            # Chunk text into sentences for interruptibility
            sentences = [s.strip() for s in text.replace(".", ".\n").split("\n") if s.strip()]

            for sentence in sentences:
                if self._interrupt_flag.is_set():
                    self._set_state(VoiceStreamState.INTERRUPTED)
                    return

                # Generate and play each sentence
                output_file = f"_tts_chunk_{uuid.uuid4().hex[:8]}.mp3"
                asyncio.run(self._generate_tts(sentence, output_file))

                if os.path.exists(output_file):
                    self._play_audio(output_file)
                    os.remove(output_file)

        except Exception as e:
            print(f"[Voice] TTS error: {e}")
        finally:
            if not self._interrupt_flag.is_set():
                self._set_state(VoiceStreamState.IDLE)

    async def _generate_tts(self, text: str, output_file: str):
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_file)

    def _play_audio(self, filepath: str):
        """Play audio file. Uses system player as fallback."""
        try:
            if os.name == "nt":
                os.system(f'start /min "" "ffplay" -nodisp -autoexit "{filepath}" 2>NUL')
            else:
                os.system(f'ffplay -nodisp -autoexit "{filepath}" 2>/dev/null &')
            # Wait for approximate duration
            file_size = os.path.getsize(filepath)
            duration = max(0.5, file_size / 16000)  # rough estimate
            elapsed = 0.0
            while elapsed < duration and not self._interrupt_flag.is_set():
                time.sleep(0.1)
                elapsed += 0.1
        except Exception:
            pass

    def stop_speaking(self):
        """Interrupt current speech."""
        self._interrupt_flag.set()
        self._set_state(VoiceStreamState.INTERRUPTED)

    def interrupt(self):
        """User interrupted — stop speaking and start listening."""
        self.stop_speaking()

    # ---- STT (listening) ----

    def start_listening(self, callback: Callable[[str], None] = None):
        """Start continuous listening in background."""
        if not SR_AVAILABLE:
            print("[Voice] speech_recognition not installed")
            return

        self.on_speech_detected = callback
        self._listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._listen_thread.start()

    def _listen_loop(self):
        self._set_state(VoiceStreamState.LISTENING)

        try:
            mic = sr.Microphone()
            with mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                while self.state != VoiceStreamState.IDLE:
                    if self.state == VoiceStreamState.SPEAKING:
                        time.sleep(0.2)
                        continue

                    try:
                        audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=15)
                        self._set_state(VoiceStreamState.PROCESSING)

                        text = self.recognizer.recognize_google(audio)

                        if text and self.on_speech_detected:
                            # If AI is speaking, this is an interruption
                            if self.state == VoiceStreamState.SPEAKING:
                                self.interrupt()

                            self.on_speech_detected(text)

                    except sr.WaitTimeoutError:
                        pass
                    except sr.UnknownValueError:
                        pass
                    except Exception as e:
                        print(f"[Voice] Listen error: {e}")

                    self._set_state(VoiceStreamState.LISTENING)

        except Exception as e:
            print(f"[Voice] Microphone error: {e}")

    def stop_listening(self):
        self._set_state(VoiceStreamState.IDLE)

    def set_voice(self, voice: str):
        self.voice = self.VOICES.get(voice, voice)

    def get_available_voices(self) -> Dict[str, str]:
        return dict(self.VOICES)


# =============================================================================
# INTERACTIVE CANVAS — dynamic UI component generation
# =============================================================================

class CanvasComponentType(Enum):
    CHART = "chart"
    TABLE = "table"
    FORM = "form"
    SLIDER = "slider"
    BUTTON = "button"
    TEXT = "text"
    IMAGE = "image"
    CODE = "code"
    PROGRESS = "progress"
    METRIC_CARD = "metric_card"
    CALCULATOR = "calculator"
    TIMER = "timer"
    CHECKLIST = "checklist"


@dataclass
class CanvasComponent:
    component_id: str
    component_type: CanvasComponentType
    props: Dict[str, Any]
    position: Dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0, "w": 400, "h": 300})
    interactive: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class InteractiveCanvas:
    """Generate dynamic, interactive UI components inside the chat."""

    def __init__(self):
        self.components: Dict[str, CanvasComponent] = {}
        self.event_handlers: Dict[str, Callable] = {}
        self.lock = threading.Lock()

    def add_chart(self, chart_type: str, data: Dict[str, Any], title: str = "", **kwargs) -> str:
        """Add a chart (bar, line, pie, scatter)."""
        return self._add(CanvasComponentType.CHART, {
            "chart_type": chart_type, "data": data, "title": title, **kwargs,
        })

    def add_table(self, headers: List[str], rows: List[List[Any]], title: str = "", **kwargs) -> str:
        """Add a data table."""
        return self._add(CanvasComponentType.TABLE, {
            "headers": headers, "rows": rows, "title": title, **kwargs,
        })

    def add_form(self, fields: List[Dict[str, Any]], submit_label: str = "Submit", on_submit: Callable = None) -> str:
        """Add an interactive form."""
        comp_id = self._add(CanvasComponentType.FORM, {
            "fields": fields, "submit_label": submit_label,
        })
        if on_submit:
            self.event_handlers[f"{comp_id}_submit"] = on_submit
        return comp_id

    def add_slider(self, min_val: float, max_val: float, step: float = 1, label: str = "",
                   on_change: Callable = None) -> str:
        comp_id = self._add(CanvasComponentType.SLIDER, {
            "min": min_val, "max": max_val, "step": step, "label": label, "value": min_val,
        })
        if on_change:
            self.event_handlers[f"{comp_id}_change"] = on_change
        return comp_id

    def add_button(self, label: str, on_click: Callable = None, style: str = "primary") -> str:
        comp_id = self._add(CanvasComponentType.BUTTON, {"label": label, "style": style})
        if on_click:
            self.event_handlers[f"{comp_id}_click"] = on_click
        return comp_id

    def add_metric_card(self, title: str, value: Any, unit: str = "", trend: str = "", icon: str = "") -> str:
        return self._add(CanvasComponentType.METRIC_CARD, {
            "title": title, "value": value, "unit": unit, "trend": trend, "icon": icon,
        })

    def add_progress(self, label: str, value: float, max_value: float = 100) -> str:
        return self._add(CanvasComponentType.PROGRESS, {
            "label": label, "value": value, "max": max_value,
        })

    def add_code(self, code: str, language: str = "python") -> str:
        return self._add(CanvasComponentType.CODE, {"code": code, "language": language})

    def add_checklist(self, items: List[Dict[str, Any]], title: str = "") -> str:
        return self._add(CanvasComponentType.CHECKLIST, {"items": items, "title": title})

    def add_timer(self, duration_seconds: int, label: str = "Timer") -> str:
        return self._add(CanvasComponentType.TIMER, {
            "duration": duration_seconds, "label": label, "started_at": datetime.now().isoformat(),
        })

    def update_component(self, component_id: str, updates: Dict[str, Any]):
        with self.lock:
            comp = self.components.get(component_id)
            if comp:
                comp.props.update(updates)

    def remove_component(self, component_id: str):
        with self.lock:
            self.components.pop(component_id, None)

    def handle_event(self, component_id: str, event_type: str, event_data: Any = None) -> Any:
        handler = self.event_handlers.get(f"{component_id}_{event_type}")
        if handler:
            return handler(event_data)
        return None

    def render_all(self) -> List[Dict[str, Any]]:
        """Get all components for frontend rendering."""
        with self.lock:
            return [
                {"id": c.component_id, "type": c.component_type.value, "props": c.props,
                 "position": c.position, "interactive": c.interactive}
                for c in self.components.values()
            ]

    def clear(self):
        with self.lock:
            self.components.clear()
            self.event_handlers.clear()

    def _add(self, ctype: CanvasComponentType, props: Dict[str, Any]) -> str:
        comp = CanvasComponent(
            component_id=uuid.uuid4().hex[:10],
            component_type=ctype,
            props=props,
        )
        with self.lock:
            self.components[comp.component_id] = comp
        return comp.component_id


# =============================================================================
# PROACTIVE NOTIFICATION & BACKGROUND TASK SYSTEM
# =============================================================================

class NotificationPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Notification:
    notification_id: str
    title: str
    message: str
    priority: NotificationPriority
    source: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    read: bool = False
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BackgroundMonitor:
    monitor_id: str
    name: str
    check_fn: Callable
    interval_seconds: int
    condition_fn: Callable
    notification_template: str
    active: bool = True
    last_check: Optional[str] = None
    last_triggered: Optional[str] = None


class ProactiveNotificationSystem:
    """Run background monitors and push notifications when conditions are met."""

    def __init__(self):
        self.notifications: List[Notification] = []
        self.monitors: Dict[str, BackgroundMonitor] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.on_notification: Optional[Callable[[Notification], None]] = None
        self.lock = threading.Lock()

    def add_monitor(
        self,
        name: str,
        check_fn: Callable,
        condition_fn: Callable,
        interval_seconds: int = 60,
        notification_template: str = "Alert: {name}",
    ) -> str:
        """Register a background monitor."""
        monitor = BackgroundMonitor(
            monitor_id=uuid.uuid4().hex[:10],
            name=name,
            check_fn=check_fn,
            interval_seconds=interval_seconds,
            condition_fn=condition_fn,
            notification_template=notification_template,
        )
        with self.lock:
            self.monitors[monitor.monitor_id] = monitor
        return monitor.monitor_id

    def remove_monitor(self, monitor_id: str):
        with self.lock:
            self.monitors.pop(monitor_id, None)

    def start(self):
        """Start background monitoring loop."""
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _monitor_loop(self):
        while self._running:
            now = datetime.now()

            with self.lock:
                monitors = list(self.monitors.values())

            for monitor in monitors:
                if not monitor.active:
                    continue

                # Check timing
                if monitor.last_check:
                    last = datetime.fromisoformat(monitor.last_check)
                    if (now - last).total_seconds() < monitor.interval_seconds:
                        continue

                monitor.last_check = now.isoformat()

                try:
                    result = monitor.check_fn()
                    if monitor.condition_fn(result):
                        self._push_notification(
                            title=monitor.name,
                            message=monitor.notification_template.format(name=monitor.name, result=result),
                            priority=NotificationPriority.HIGH,
                            source=f"monitor:{monitor.monitor_id}",
                            data={"result": result},
                        )
                        monitor.last_triggered = now.isoformat()
                except Exception as e:
                    print(f"[Monitor] {monitor.name} error: {e}")

            time.sleep(1)

    def _push_notification(self, title: str, message: str, priority: NotificationPriority,
                           source: str, data: Dict[str, Any] = None):
        notif = Notification(
            notification_id=uuid.uuid4().hex[:10],
            title=title,
            message=message,
            priority=priority,
            source=source,
            data=data or {},
        )
        with self.lock:
            self.notifications.append(notif)

        if self.on_notification:
            self.on_notification(notif)

    def push(self, title: str, message: str, priority: str = "medium", data: Dict[str, Any] = None) -> str:
        """Manually push a notification."""
        self._push_notification(title, message, NotificationPriority(priority), "manual", data)
        return "Notification pushed"

    def get_unread(self) -> List[Dict[str, Any]]:
        with self.lock:
            return [asdict(n) for n in self.notifications if not n.read]

    def mark_read(self, notification_id: str):
        with self.lock:
            for n in self.notifications:
                if n.notification_id == notification_id:
                    n.read = True

    def mark_all_read(self):
        with self.lock:
            for n in self.notifications:
                n.read = True

    def get_all(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.lock:
            return [asdict(n) for n in self.notifications[-limit:]]


# =============================================================================
# GLOBAL INSTANCES
# =============================================================================

voice_engine = VoiceStreamEngine()
canvas = InteractiveCanvas()
notification_system = ProactiveNotificationSystem()


__all__ = [
    "VoiceStreamEngine",
    "VoiceStreamState",
    "InteractiveCanvas",
    "CanvasComponentType",
    "CanvasComponent",
    "ProactiveNotificationSystem",
    "Notification",
    "NotificationPriority",
    "BackgroundMonitor",
    "voice_engine",
    "canvas",
    "notification_system",
]
