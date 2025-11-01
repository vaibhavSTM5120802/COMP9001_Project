# src/launcher.py
# Tkinter GUI launcher that runs voice / gesture in separate Processes
# Works both in dev and in PyInstaller EXE.

import tkinter as tk
from tkinter import messagebox
from multiprocessing import Process, freeze_support, set_start_method
import sys

# import modules directly (PyInstaller bundles them)
import voice
import gesture

voice_proc: Process | None = None
gest_proc: Process | None = None

def start_voice():
    global voice_proc
    if voice_proc and voice_proc.is_alive():
        messagebox.showinfo("Info", "🎙️ Voice already running.")
        return
    try:
        voice_proc = Process(target=voice.main, daemon=True)
        voice_proc.start()
        status_var.set("Voice: RUNNING")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start Voice:\n{e}")

def stop_voice():
    global voice_proc
    if voice_proc and voice_proc.is_alive():
        voice_proc.terminate()
        voice_proc.join(timeout=1)
    voice_proc = None
    status_var.set("Voice: STOPPED")

def start_gesture():
    global gest_proc
    if gest_proc and gest_proc.is_alive():
        messagebox.showinfo("Info", "🖐 Gesture already running.")
        return
    try:
        gest_proc = Process(target=gesture.main, daemon=True)
        gest_proc.start()
        status_var2.set("Gesture: RUNNING")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start Gesture:\n{e}")

def stop_gesture():
    global gest_proc
    if gest_proc and gest_proc.is_alive():
        gest_proc.terminate()
        gest_proc.join(timeout=1)
    gest_proc = None
    status_var2.set("Gesture: STOPPED")

def on_close():
    stop_voice()
    stop_gesture()
    root.destroy()

if __name__ == "__main__":  # IMPORTANT for Windows multiprocessing
    # For PyInstaller + Windows multiprocessing
    freeze_support()
    try:
        set_start_method("spawn")
    except RuntimeError:
        # already set by parent / environment
        pass

    # --- UI setup ---
    root = tk.Tk()
    root.title("Meet Controller — Launcher")
    root.geometry("520x240")

    title = tk.Label(root, text="🎛️ Meet Controller", font=("Segoe UI", 20, "bold"))
    title.pack(pady=8)

    # Voice controls
    row1 = tk.Frame(root)
    row1.pack(pady=6)
    tk.Button(row1, text="Start Voice", width=18, command=start_voice).pack(side=tk.LEFT, padx=10)
    tk.Button(row1, text="Stop Voice", width=18, command=stop_voice).pack(side=tk.LEFT, padx=10)

    # Gesture controls
    row2 = tk.Frame(root)
    row2.pack(pady=6)
    tk.Button(row2, text="Start Gesture", width=18, command=start_gesture).pack(side=tk.LEFT, padx=10)
    tk.Button(row2, text="Stop Gesture", width=18, command=stop_gesture).pack(side=tk.LEFT, padx=10)

    # Info + status labels
    tk.Label(root, text="Open your Google Meet first, then start a mode.",
             font=("Segoe UI", 10)).pack(pady=8)

    status_var = tk.StringVar(value="Voice: STOPPED")
    status_var2 = tk.StringVar(value="Gesture: STOPPED")
    tk.Label(root, textvariable=status_var, fg="green", font=("Segoe UI", 9)).pack()
    tk.Label(root, textvariable=status_var2, fg="green", font=("Segoe UI", 9)).pack()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
