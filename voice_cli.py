"""
SweetyAI Voice & CLI Command Engine
Listens via microphone (or accepts text commands) to trigger legal workstation tasks.

Voice intents are mapped onto the unified Google Workspace connector:
  - "schedule hearing ..." -> Calendar event
  - "task / file ..."      -> Google Tasks to-do
"""

import sys
import argparse

try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except Exception:
    sr = None
    SPEECH_AVAILABLE = False

try:
    from google_workspace_connector import GoogleWorkspaceConnector
    GWC_AVAILABLE = True
except Exception:
    GoogleWorkspaceConnector = None
    GWC_AVAILABLE = False


def listen_to_voice():
    """Captures audio from the microphone and converts it to text."""
    if not SPEECH_AVAILABLE:
        print("[SweetyAI Voice] speech_recognition not installed. Run: pip install SpeechRecognition")
        return None

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("[SweetyAI Voice] Adjusting for ambient noise... Please speak your command.")
        r.adjust_for_ambient_noise(source, duration=1)
        print("[SweetyAI Voice] Listening now...")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            text = r.recognize_google(audio)
            print(f"[SweetyAI Voice] Recognized: '{text}'")
            return text
        except sr.WaitTimeoutError:
            print("[SweetyAI Voice] Listening timed out. No speech detected.")
        except sr.UnknownValueError:
            print("[SweetyAI Voice] Could not understand audio.")
        except sr.RequestError as e:
            print(f"[SweetyAI Voice] Could not request results from speech service: {e}")
    return None


def _connector():
    """Instantiate and authenticate the Google Workspace connector (best effort)."""
    if not GWC_AVAILABLE:
        print("[SweetyAI Voice Engine] google_workspace_connector unavailable.")
        return None
    try:
        conn = GoogleWorkspaceConnector()
        conn.authenticate()
        return conn
    except Exception as e:
        print(f"[SweetyAI Voice Engine] Google Workspace authentication failed: {e}")
        return None


def parse_voice_command(command_str):
    """Maps spoken phrases to workspace actions (calendar hearing / filing task)."""
    command_str = command_str.lower()

    if "hearing" in command_str or "schedule" in command_str:
        print("[SweetyAI Voice Engine] Mapping voice input to Calendar Hearing...")
        conn = _connector()
        if conn:
            conn.create_calendar_event(
                summary="Hearing: Voice Scheduled Case",
                start_time="2026-11-28T10:30:00+05:30",
                end_time="2026-11-28T11:00:00+05:30",
                description=f"Voice command: {command_str}",
            )
    elif "task" in command_str or "file" in command_str:
        print("[SweetyAI Voice Engine] Mapping voice input to Google Task...")
        conn = _connector()
        if conn:
            conn.add_to_do_task(
                task_title="Voice-logged filing task",
                due_date="2026-10-30",
                notes=f"Voice command: {command_str}",
            )
    else:
        print(f"[SweetyAI Voice Engine] Unrecognized command intent: '{command_str}'")
        print("Try: 'schedule hearing ...' or 'file a task ...'")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="voice_cli.py", description="SweetyAI voice / text command engine")
    parser.add_argument("--voice", action="store_true", help="Capture a command from the microphone")
    parser.add_argument("command", nargs="*", help="Text command (alternative to --voice)")
    args = parser.parse_args(argv)

    if args.voice:
        spoken_text = listen_to_voice()
        if spoken_text:
            parse_voice_command(spoken_text)
    elif args.command:
        parse_voice_command(" ".join(args.command))
    else:
        print("Usage: python3 voice_cli.py --voice   (or: python3 voice_cli.py 'schedule hearing tomorrow')")


if __name__ == "__main__":
    main()
