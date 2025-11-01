# src/meetfocus.py
from pathlib import Path
from config import load_shortcuts
from focus import focus_window_by_hints

BASE_DIR = Path(__file__).resolve().parent.parent  # project root
CONF_PATH = BASE_DIR / "config" / "shortcuts.yaml"

if __name__ == "__main__":
    conf = load_shortcuts(CONF_PATH)
    # quick sanity
    # print(conf)
    hints = conf["apps"]["meet"]["window_hints"]
    ok = focus_window_by_hints(hints)                      
    print("Focused Meet:", ok)
