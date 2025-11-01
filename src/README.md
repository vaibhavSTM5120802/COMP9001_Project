
# Google Meet Voice & Gesture Controller

## Project Description
Google Meet Voice & Gesture Controller is a Python-based automation software that is designed to boost productivity in Google Meet.
It automatically detects any active Google Meet window, and allows users to control it through voice commands or optional hand controls with OpenCV.

The aim of this project is to offer touchless interaction — Facilitates muting/unmuting of the microphone, turning the camera on/off, all by using natural intuitive inputs.

### Key Features
- **Voice Control:** Execute Meet functions via spoken commands (e.g., "mute", "camera off", "exit").
- **Gesture Support:** OpenCV module to recognise basic hand gestures (e.g., palm/fist actions).
- **Auto-Detect Meet Window:** Finds and focuses the browser tab with an active meeting.
- **Cross-Library Integration:** Uses PyAudio, SpeechRecognition, PyAutoGUI, and PyGetWindow for smooth automation.
- **User Feedback:** Console-based messages for live status updates.

---

## Installation


### Dependencies
- opencv-python
- SpeechRecognition
- PyAudio
- PyAutoGUI
- PyGetWindow
- pywinauto
- keyboard



### Prerequisites
- Windows 10 / 11  
- Python 3.10 or newer  
- Functional microphone  
- Functional Camera

### Steps
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. If PyAudio installation fails:
   ```bash
   pip install pipwin
   pipwin install pyaudio
   ```
### Run
   1. Open/join a Google Meet in your browser.  
   2. In PowerShell (with the venv active), run:
      ```powershell
      python src\luncher.py
      ```
   3. launcher will pop up and then start the action like (start voice/ gesture)
---

## Usage

1. Open an active Google Meet session in your browser.  
2. Run the script:
   ```bash
   python src/luncher.py
   ```
3. When Voice control active…" appears, say one of the supported commands:
   - "mute" / "unmute" / "toggle mute"  
   - "camera on" / "camera off"    
   - "exit" / "quit"  

4. How it's works
   1. The app detects the active Meet window.
   2. Listens for voice or gesture input.
   3. Executes keyboard shortcuts (Ctrl + D, Ctrl + E) accordingly.

### Demo Video

---

## Authors and Acknowledgments
**Author:** Vaibhav Sawant 
**Institution:** University Of Sydney 
**Acknowledgments:**  
- Open-source Python community for PyAudio, SpeechRecognition, PyAutoGUI, and OpenCV libraries.  
- Google Meet documentation for official keyboard shortcuts used in automation.

---

## Known Issues & Future Features
### Known Issues
- Hotkey behaviour may vary depending on browser or language layout.
- Multiple open Meet tabs can cause the wrong window to activate.

### Future Features
- Full integration of gesture control using MediaPipe for better accuracy.  
- GUI overlay to show real-time mic/camera status.  
- Configurable voice commands and shortcut remapping.
-


Project/
├── config/
│   └── settings.yaml
├── models/
│   └── gesture_model.onnx
├── src/
│   ├── launcher.py
│   ├── voice_module.py
│   ├── gesture_module.py
│   └── meetfocus.py
└── requirements.txt
