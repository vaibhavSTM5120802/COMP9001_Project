# src/focus.py  
# bring google meet window to foreground

import time
from typing import List

import pygetwindow as gw                                  # find windowsby title to activate them

try:
    import win32gui, win32con
except Exception:
    win32gui = None
    win32con = None

try:
    from pywinauto import Desktop, Application
except Exception:
    Desktop = None
    Application = None


def _best_meet_title(hints: List[str]) -> str | None:                                                 # pick the most likely Google Meet window title using patterns, then hints
    titles = [t for t in gw.getAllTitles() if t and t.strip()]
    if not titles:
        return None

    tl = [(t, t.lower()) for t in titles]
    c1, c2, c3 = [], [], []

    for orig, low in tl:
        if ".meet.google.com" in low:
            c1.append(orig)
            continue
        if (" meet " in f" {low} " or low.startswith("meet ") or "google meet" in low
            or "meet -" in low or "meet —" in low or "meet:" in low):
            c2.append(orig)
            continue
        if any(h.lower() in low for h in hints):
            c3.append(orig)

    for bucket in (c1, c2, c3):
        if bucket:
            return bucket[0]
    return None


def _foreground_with_win32(title: str) -> bool:                     #enumerate top-level windows and SetForegroundWindow         
    if not win32gui:
        return False
    try:
        def _enum_handler(hwnd, acc):
            if win32gui.IsWindowVisible(hwnd):
                text = win32gui.GetWindowText(hwnd)
                if text and title in text:
                    acc.append(hwnd)
        found = []
        win32gui.EnumWindows(_enum_handler, found)
        if not found:
            return False

        hwnd = found[0]
        
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.25)
        return True
    except Exception:
        return False


def _foreground_with_pygetwindow(title: str) -> bool:               #activate exact-title match via pygetwindow
    try:
        w = gw.getWindowsWithTitle(title)
        if not w:
            return False
        w = w[0]
        if w.isMinimized:
            w.restore()
        w.activate()
        time.sleep(0.25)
        return True
    except Exception:
        return False


def _foreground_with_pywinauto(hints: List[str], timeout: float = 2.0) -> bool:                   #search desktop windows by meet patterns, else by hints; set focus
    if not Desktop:
        return False
    try:
        app = Desktop(backend="uia")
        wins = app.windows()
        for w in wins:
            try:
                text = w.window_text() or ""
                if any(h.lower() in text.lower() for h in hints):
                    w.set_focus()
                    time.sleep(0.25)
                    return True
            except Exception:
                continue
    except Exception:
        pass
    
    try:
        app = Application(backend="uia").connect(title_re=".*", timeout=timeout)
        for ww in app.windows():
            title = ww.window_text()
            if title and any(h.lower() in title.lower() for h in hints):
                try:
                    ww.set_focus()
                    time.sleep(0.25)
                    return True
                except Exception:
                    continue
    except Exception:
        pass
    return False


def focus_window_by_hints(hints: List[str]) -> bool:
    """
    Main entry used by voice/gesture. Returns True if focus succeeded.
    """

    target = _best_meet_title(hints)
    if not target:
        return False
    if _foreground_with_pygetwindow(target):
        return True
    if _foreground_with_win32(target):
        return True
    if _foreground_with_pywinauto(hints):
        return True

    return False
