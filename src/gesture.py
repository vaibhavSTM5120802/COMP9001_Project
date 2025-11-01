
from pathlib import Path                                     # used to handle file and folder paths safely
import time                                                  # used to create small delays, e.g., to stabilize gesture detection or focus timing.

import cv2                                                   #used to access camera frames and perform image processing for hand detection.
import mediapipe as mp                                      #detects and tracks hand landmarks for gesture recognition.
import pyautogui                                            #automates keyboard/mouse actions
 
from config import load_shortcuts                          
from focus import focus_window_by_hints


BASE_DIR   = Path(__file__).resolve().parent.parent
CONF_PATH  = BASE_DIR / "config" / "shortcuts.yaml"
APP_KEY    = "meet"              

PREF_INDEX = 0                   
MIN_DET    = 0.6                 
MIN_TRK    = 0.6                

HOLD_TIME  = 0.5                   ## seconds: how long a gesture must be held before triggering
COOLDOWN   = 0.8                 # seconds: lockout after a trigger to prevent double-fires

def send_hotkey(keys: list[str]):
    pyautogui.hotkey(*keys)


TIP_IDS = [8, 12, 16, 20]  
PIP_IDS = [6, 10, 14, 18]   

def count_extended_fingers(lm):
    #Return how many (of 4: index..pinky) look extended.
    cnt = 0
    for tip, pip in zip(TIP_IDS, PIP_IDS):
        if lm[tip].y < lm[pip].y:
            cnt += 1
    return cnt

def is_open_palm(lm, thresh=3):
    return count_extended_fingers(lm) >= thresh

def is_fist(lm, thresh=1):
    return count_extended_fingers(lm) <= thresh


def open_camera():
    """
    Try to open laptop's default camera at index 0 with common Windows backends.
    Fallback: scan a few indexes/backends if needed.
    """
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]

    for backend in backends:
        cap = cv2.VideoCapture(PREF_INDEX, backend)
        if cap.isOpened():
            ok, _ = cap.read()
            if ok:
                print(f"[INFO] Using camera index {PREF_INDEX} backend {backend}")
                return cap
            cap.release()

    for backend in backends:
        for idx in (0, 1, 2, 3):
            cap = cv2.VideoCapture(idx, backend)
            if cap.isOpened():
                ok, _ = cap.read()
                if ok:
                    print(f"[INFO] Using camera index {idx} backend {backend}")
                    return cap
                cap.release()
    return None


def main():
    # Load shortcuts/config
    conf = load_shortcuts(CONF_PATH)
    meet = conf["apps"][APP_KEY]
    HINTS    = meet["window_hints"]
    MIC_KEYS = meet["mic"]
    CAM_KEYS = meet["cam"]


    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=MIN_DET,
        min_tracking_confidence=MIN_TRK,
    )
    mp_draw = mp.solutions.drawing_utils
    draw_style = mp.solutions.drawing_styles


    cap = open_camera()
    if cap is None:
        raise RuntimeError(
            "Webcam not accessible.\n"
            "- Windows Settings → Privacy & security → Camera → VS Code/Terminal"
        )

    last_action_time = 0.0      # timestamp of the last gesture-triggered action
    current_gesture = None       
    current_start   = 0.0   #current gesture started

    print("Gesture control ready. Open palm = mic toggle, Fist = camera toggle")
    print("Press 'q' to quit.")

    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.02)
            continue

        # Mirror view
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = hands.process(rgb)

        detected = None  # "open" / "fist" / None

        if res.multi_hand_landmarks:
            lm_list = res.multi_hand_landmarks[0].landmark

            if is_open_palm(lm_list):
                detected = "open"
            elif is_fist(lm_list):
                detected = "fist"

            # draw landmarks
            mp_draw.draw_landmarks(
                frame, res.multi_hand_landmarks[0],
                mp_hands.HAND_CONNECTIONS,
                draw_style.get_default_hand_landmarks_style(),
                draw_style.get_default_hand_connections_style()
            )

        # Gesture hold + cooldown logic
        now = time.time()
        if detected is None:
            current_gesture = None
            current_start = 0.0
        else:
            if detected != current_gesture:
                current_gesture = detected
                current_start = now

            held_for = now - current_start if current_start else 0.0
            cooled   = (now - last_action_time) >= COOLDOWN

            if held_for >= HOLD_TIME and cooled:
                # Focus Meet first
                action_text = ""
                if focus_window_by_hints(HINTS):
                    if current_gesture == "open":      # mic toggle
                        send_hotkey(MIC_KEYS)
                        action_text = "Mic toggled"
                    else:                               # "fist" => cam toggle
                        send_hotkey(CAM_KEYS)
                        action_text = "Camera toggled"
                    last_action_time = now
                else:
                    action_text = "Could not focus Meet"

                # On-frame feedback
                cv2.putText(frame, action_text, (20, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                # Reset so user must show gesture again
                current_gesture = None
                current_start = 0.0

        # UI overlays
        if detected:
            cv2.putText(frame, f"Gesture: {detected}", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        cv2.imshow("Gesture Control (press q to quit)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    hands.close()

if __name__ == "__main__":
    main()
