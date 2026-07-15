# Visually Impaired Road Crossing Assistant

> **Work in Progress** — The core pipeline is functional. Custom YOLOv8 model training on the India Driving Dataset is ongoing (4 of 7 rounds complete). This page will be updated as training finishes.

---

## What This Project Does

Crossing a road in an Indian city is chaotic even for someone with full vision. For a visually impaired person, it's genuinely dangerous — mixed traffic, no lane discipline, signals that get ignored. This project is an attempt to build an assistant that can help with exactly that.

The system watches the road through a camera, detects what's around (vehicles, traffic lights, pedestrians), and tells the user whether it's safe to cross — out loud, in their language. They can also ask questions like "is anything coming from the left?" and get a spoken response.

---

## How It Works

The pipeline has four stages:

**1. Detection** — A YOLOv8n model (fine-tuned on Indian road footage) processes each camera frame and identifies vehicles, traffic lights, and pedestrians in real time.

**2. Scene Building** — Detections are converted into a plain English description of the current road situation, for example: *"Traffic light is red. 3 vehicles detected: Car, Two Wheeler, Large Vehicle."*

**3. Understanding** — That scene description is sent to LLaMA 3.3 70B (via Groq API), which interprets it and generates a natural, context-aware safety response.

**4. Voice Output** — The response is spoken aloud using pyttsx3 (English) or gTTS (Hindi/Telugu). The user can ask follow-up questions via microphone at any time.

The camera runs on a background thread so detection is continuous, while the main thread handles the voice conversation. A threading lock keeps the shared scene state safe between the two.

---

## Why a Custom Model?

Standard YOLOv8 is trained on COCO — a dataset built mostly from Western roads. It doesn't handle auto-rickshaws, heavily loaded two-wheelers, or the general unpredictability of Indian traffic particularly well.

The fix is to fine-tune on the **India Driving Dataset (IDD)**, which was collected specifically from Indian roads across multiple cities. Training is progressive — starting with a small subset and scaling up — so we can evaluate improvement at each stage before committing to the next round on Colab.

| Round | Images | Status |
|---|---|---|
| v1 | 1,000 | Done |
| v2 | 5,000 | Done |
| v3 | 10,000 | Done |
| v4a | 15,000 | Done — active model |
| v4b | 20,000 | Pending |
| v5a | 25,000 | Pending |
| v5b | 30,000 | Pending |

---

## Tech Stack

- **YOLOv8n** (Ultralytics) — object detection
- **LLaMA 3.3 70B** via Groq API — scene understanding and response generation
- **OpenCV** — frame capture and bounding box rendering
- **pyttsx3** — offline English TTS (Windows SAPI5)
- **gTTS + playsound** — online TTS for Hindi and Telugu
- **SpeechRecognition** — microphone input via Google Speech API

---

## Languages Supported

English (en-IN), Hindi (hi-IN), and Telugu (te-IN). On startup, the user says ONE, TWO, or THREE to pick their language. Everything after that — prompts, responses, confirmations — comes in that language.

---

## Getting Started

**Clone the repo**
```bash
git clone https://github.com/janapati2005/road-crossing-assistant.git
cd road-crossing-assistant
```

**Install dependencies**
```bash
pip install -r requirements.txt
```

**Set your Groq API key** (get one free at console.groq.com)
```bash
# Windows
setx GROQ_API_KEY "your_key_here"
```
Close and reopen your terminal after running this.

**Set your video source** — open `assistant2.py` and update line 171:
```python
# Use a video file for testing:
cap = cv2.VideoCapture(r"path\to\traffic_video.mp4")

# Or switch to live webcam:
cap = cv2.VideoCapture(0)
```

**Add model weights** — place `best_v4a.pt` in the project root. *(Download link will be added once training is complete.)*

**Run**
```bash
python assistant2.py
```

---

## Project Structure

```
road-crossing-assistant/
├── assistant2.py        # Main application
├── requirements.txt
├── README.md
├── tests/
│   ├── test_groq.py     # Verify Groq API connection
│   ├── test_mic.py      # Basic microphone test
│   ├── test_mic2.py     # Mic test with custom sensitivity
│   └── test_speak.py    # Voice output test
└── archive/
    └── assistant_v1.py  # Earlier single-threaded version
```

If you want to test individual components before running the full system, start with `tests/test_groq.py` to confirm your API key works, then `tests/test_speak.py` for audio, then `tests/test_mic.py` for microphone input.

---

## Known Issues

**pyttsx3 silent failure on Windows** — reusing the same engine instance across multiple calls causes it to stop speaking without throwing any error. The fix is to initialize a fresh engine on every call, which is what the current code does.

**Traffic light color detection** — works reasonably well in good lighting but can be unreliable at night or with non-standard signal placements. This will improve as the custom model training progresses.

---

## What's Next

- Finish training rounds v4b through v5b and swap in the final model
- Move from video file input to live webcam as the default
- Add rough distance estimation for detected vehicles
- Field test with actual visually impaired users and incorporate feedback

---

## Author

Janapati Hari Aditya  
B.Tech Computer Science and Engineering  
Amrita Vishwa Vidyapeetham, Amaravati  
[github.com/janapati2005](https://github.com/janapati2005)
