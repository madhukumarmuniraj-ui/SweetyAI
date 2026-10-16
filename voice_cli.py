"""
SweetyAI Voice & CLI Command Engine
Listens via microphone (or accepts text commands) to trigger legal workstation tasks.
"""

import sys
import argparse
import speech_recognition as sr
from sweety_core import main as core_main

def listen_to_voice():
    """Captures audio from the microphone and converts it to text."""
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

def parse_voice_command(command_str):
    """Maps spoken phrases to CLI arguments for sweety_core."""
    command_str = command_str.lower()
    
    # Example voice command: "schedule hearing for writ petition 9999 on November 25"
    if "hearing" in command_str or "schedule" in command_str:
        print("[SweetyAI Voice Engine] Mapping voice input to Calendar Hearing...")
        # For demonstration, trigger a default hearing via sys.argv injection
        sys.argv = [
            "sweety_core.py", 
            "hearing", 
            "--title", "Hearing: Voice Scheduled Case", 
            "--start", "2026-11-28T10:30:00+05:30", 
            "--end", "2026-11-28T11:00:00+05:30"
        ]
        core_main()
    elif "task" in command_str or "file" in command_str:
        print("[SweetyAI Voice Engine] Mapping voice input to Google Task...")
        sys.argv = [
            "sweety_core.py", 
            "task", 
            "--title", "Voice-logged filing task", 
            "--due", "2026-10-30"
        ]
        core_main()
    else:
        print(f"[SweetyAI Voice Engine] Unrecognized command intent: '{command_str}'")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--voice":
        spoken_text = listen_to_voice()
        if spoken_text:
            parse_voice_command(spoken_text)
    else:
        print("Usage: python3 voice_cli.py --voice (or use custom terminal shortcuts)")
