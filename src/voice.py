# src/voice.py
from pathlib import Path
import queue, json, time

import pyautogui
import sounddevice as sd                             # microphone input stream
from vosk import Model, KaldiRecognizer              # Offline model to dected the words

from config import load_shortcuts
from focus import focus_window_by_hints

BASE_DIR    = Path(__file__).resolve().parent.parent    
CONF_PATH   = BASE_DIR / "config" / "shortcuts.yaml"
MODEL_DIR   = BASE_DIR / "models" / "vosk-small"      
APP_KEY     = "meet"          
SAMPLE_RATE = 16000                                        #default audio sampling rate in Hz for recognizer
BLOCKSIZE   = 8000                                         # audio chunk size
DRY_RUN     = False           
WAKE_WORD   = None          


def send_hotkey(keys: list[str]):
    """Send a hotkey like ['ctrl','d'] using pyautogui."""
    if DRY_RUN:
        print(f"(dry-run) would send hotkey: {keys}")
        return
    pyautogui.hotkey(*keys)


def text_to_intent(text: str):
    """
    Map recognized text to an intent:
    returns 'toggle_mic', 'toggle_cam', 'exit', or None.
    """
    t = (text or "").lower().strip()
    if not t:
        return None

    if WAKE_WORD:                                                         #use any special word to start for e.g - computer mute computer id a wake word
        if not t.startswith(WAKE_WORD + " "):
            return None
        t = t[len(WAKE_WORD) + 1:].strip()

    
    if t in {"stop", "exit", "quit", "close"}:
        return "exit"

    
    if "unmute" in t:
        return "toggle_mic"
    if "mute" in t and "un" not in t:
        return "toggle_mic"
    if "toggle mute" in t:
        return "toggle_mic"
    if "mick" in t:
        return "toggle_mic"

    if "camera on" in t or "video on" in t:
        return "toggle_cam"
    if "camera on" in t or "video on" in t:
        return "toggle_cam"
    if "canada" in t or "video off" in t:
        return "toggle_cam"
    if "toggle camera" in t or "toggle video" in t:
        return "toggle_cam"

    if t in {"mute", "unmute"}:
        return "toggle_mic"
    if t in {"camera", "video", "cam"}:
        return "toggle_cam"

    return None


def main():
    conf = load_shortcuts(CONF_PATH)
    meet = conf["apps"][APP_KEY]
    HINTS    = meet["window_hints"]
    MIC_KEYS = meet["mic"]
    CAM_KEYS = meet["cam"]

    if not MODEL_DIR.exists():
        raise FileNotFoundError(
            f"Vosk model not found at: {MODEL_DIR}\n"
            f"Make sure you unzipped the small English model to this path."
        )
    model = Model(str(MODEL_DIR))
    rec = KaldiRecognizer(model, SAMPLE_RATE)

    q = queue.Queue()

    def audio_callback(indata, frames, time_info, status):
        q.put(bytes(indata))

    print("Voice control ready.")
    print("Say: 'mute', 'unmute', 'camera off', 'camera on', 'toggle camera'")
    print("Say: 'stop' / 'exit' / 'quit' to close the program.")
    if WAKE_WORD:
        print(f"(use wake word first: '{WAKE_WORD} ...')")

    with sd.RawInputStream(samplerate=SAMPLE_RATE,
                           blocksize=BLOCKSIZE,
                           dtype='int16',
                           channels=1,
                           callback=audio_callback):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                heard = result.get("text", "").strip()
                if not heard:
                    continue

                print(f"[heard] {heard}")
                intent = text_to_intent(heard)
                if not intent:
                    continue

                
                if intent == "exit":
                    print("→ exiting on voice command")
                    break

                
                if not focus_window_by_hints(HINTS):
                    print("⚠️ Could not focus Google Meet window.")
                    continue

                if intent == "toggle_mic":
                    print("→ toggling mic")
                    send_hotkey(MIC_KEYS)
                elif intent == "toggle_cam":
                    print("→ toggling camera")
                    send_hotkey(CAM_KEYS)

                time.sleep(0.25)  # small debounce

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
