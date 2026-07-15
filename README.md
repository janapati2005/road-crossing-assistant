# 🚦 Visually Impaired Road Crossing Assistant

> ⚠️ **Work in Progress** — Core pipeline functional. Custom YOLOv8 training on IDD dataset ongoing (v4a of 5 rounds complete). This README will be updated as the project progresses.

An AI-powered real-time assistant that helps visually impaired individuals safely cross roads in Indian traffic conditions. It detects vehicles and traffic signals using a custom fine-tuned deep learning model, understands the scene using a large language model, and communicates safety instructions via voice in multiple Indian languages.

---

## 🧠 How It Works

```
Camera / Video Feed
        ↓
YOLOv8n — fine-tuned on IDD (Object Detection)
        ↓
Scene Description Builder
        ↓
Groq API — LLaMA 3.3 70B (Scene Understanding + Safety Decision)
        ↓
pyttsx3 / gTTS (Voice Output in selected language)
        ↑
SpeechRecognition (Voice Input — en-IN / hi-IN / te-IN)
```

1. Camera captures real-time road footage
2. YOLOv8n (fine-tuned on India Driving Dataset) detects vehicles, pedestrians, and traffic signals
3. Detected objects are converted into a structured scene description
4. LLaMA 3.3 70B via Groq interprets the scene and decides if it is safe to cross
5. Safety instruction is spoken aloud to the user in their chosen language

---

## 🔍 Models & Tech Used

| Component | Technology |
|---|---|
| Object Detection | YOLOv8n — custom fine-tuned on IDD |
| LLM | LLaMA 3.3 70B via Groq API |
| TTS — English | pyttsx3 (offline, Windows SAPI5) |
| TTS — Hindi / Telugu | gTTS (Google Text-to-Speech) |
| Speech Input | SpeechRecognition + Google Speech API |
| Vision | OpenCV |
| Language | Python 3.10+ |

---

## 🚗 Why Custom YOLOv8n on IDD?

Standard YOLOv8 is trained on COCO (Western datasets). It struggles with:
- Auto-rickshaws, two-wheelers, mixed traffic
- Irregular lane behaviour on Indian roads
- Indian traffic signal styles and layouts

We fine-tune YOLOv8n on the **India Driving Dataset (IDD)** to handle these conditions accurately.

### IDD Training Progress

| Round | Images | Status |
|---|---|---|
| v1 | 1,000 | ✅ Done |
| v2 | 5,000 | ✅ Done |
| v3 | 10,000 | ✅ Done |
| v4a | 15,000 | ✅ Done — currently in use (`best_v4a.pt`) |
| v4b | 20,000 | 🔄 Pending |
| v5a | 25,000 | 🔄 Pending |
| v5b (final) | 30,000 | 🔄 Pending |

Training platform: Google Colab
Dataset: IDD (India Driving Dataset), Pascal VOC XML → converted to YOLO TXT format

---

## 🌐 Multilingual Support

| Language | Voice Input | Voice Output |
|---|---|---|
| English | en-IN | pyttsx3 (offline) |
| Hindi | hi-IN | gTTS |
| Telugu | te-IN | gTTS |

On startup the user says ONE / TWO / THREE to select their language.

---

## 🏗️ Key Design Decisions

**Threaded architecture**
- Camera runs in a background thread continuously updating `current_scene`
- Main thread handles voice conversation sequentially
- `threading.Lock()` used for safe shared state access

**pyttsx3 Windows fix**
- A fresh pyttsx3 engine instance is created on every `speak()` call
- Reusing the same instance causes silent failures on Windows

**Traffic light color detection**
- HSV color analysis on the detected bounding box region
- Box split into top / middle / bottom thirds
- Red checked in top, yellow in middle, green in bottom

---

## ⚙️ Setup

### 1. Clone the repository
```bash
git clone https://github.com/janapati2005/road-crossing-assistant.git
cd road-crossing-assistant
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Groq API Key (Windows)
```bash
setx GROQ_API_KEY "your_key_here"
```
Then close and reopen your terminal. Get a free key at [console.groq.com](https://console.groq.com).

### 4. Add your video or webcam
In `assistant2.py` line 171, change the video path:
```python
# For a video file:
cap = cv2.VideoCapture(r"path\to\your\traffic_video.mp4")

# For live webcam:
cap = cv2.VideoCapture(0)
```

### 5. Add your YOLOv8 weights
Place `best_v4a.pt` in the project root. Download link: *(will be added after training completes)*

### 6. Run
```bash
python assistant2.py
```

---

## 📦 requirements.txt

```
ultralytics
groq
opencv-python
pyttsx3
SpeechRecognition
pyaudio
gtts
playsound
numpy
```

---

## 📁 Project Structure

```
road-crossing-assistant/
├── assistant2.py          # Main application (current version)
├── requirements.txt
├── README.md
├── .gitignore
├── tests/
│   ├── test_groq.py       # Test Groq API connection
│   ├── test_mic.py        # Test microphone input
│   ├── test_mic2.py       # Test microphone with custom thresholds
│   └── test_speak.py      # Test pyttsx3 voice output
└── archive/
    └── assistant_v1.py    # Earlier single-threaded version
```

---

## 🧪 Testing Individual Components

```bash
# Test if Groq API key is working
python tests/test_groq.py

# Test microphone
python tests/test_mic.py

# Test voice output
python tests/test_speak.py
```

---

## 🎯 Use Case

Designed specifically for **visually impaired users navigating Indian urban roads** — where standard Western AI models fall short due to differences in traffic density, vehicle types, and road behaviour.

---

## 🔮 Planned Updates

- Complete IDD training rounds v4b → v5b (final model)
- Switch from video file to live webcam as default
- Add distance estimation for detected vehicles
- Package as a standalone portable application

---

## 👤 Author

**Janapati Hari Aditya**
B.Tech CSE, Amrita Vishwa Vidyapeetham, Amaravati
[GitHub](https://github.com/janapati2005)
