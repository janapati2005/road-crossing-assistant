import cv2
import pyttsx3
import speech_recognition as sr
import numpy as np
import threading
import os
import time
from groq import Groq
from ultralytics import YOLO
from gtts import gTTS
import playsound

# ── Speak ──────────────────────────────────────────────
def speak(text, lang="en"):
    print(f"[Speaking]: {text}")
    if lang == "en":
        e = pyttsx3.init('sapi5')
        e.setProperty('rate', 145)
        e.setProperty('volume', 1.0)
        e.say(text)
        e.runAndWait()
        e.stop()
    else:
        gtts_lang = {"hi": "hi", "te": "te"}.get(lang, "en")
        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        tts.save("temp_audio.mp3")
        playsound.playsound("temp_audio.mp3")
        try:
            os.remove("temp_audio.mp3")
        except:
            pass

# ── Listen ─────────────────────────────────────────────
def listen(timeout=8, lang="en-IN"):
    r = sr.Recognizer()
    r.energy_threshold = 50
    r.dynamic_energy_threshold = False
    with sr.Microphone() as source:
        print("[Listening...]")
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=5)
            text  = r.recognize_google(audio, language=lang)
            print(f"[Heard]: {text}")
            return text.strip()
        except:
            return None

# ── Groq ───────────────────────────────────────────────
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def ask_groq(question, scene, lang):
    lang_map  = {"en": "English", "hi": "Hindi", "te": "Telugu"}
    lang_name = lang_map.get(lang, "English")
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"""You are a warm friendly road crossing assistant helping a visually impaired person cross the road safely in India.
Current road scene: {scene}
CRITICAL: Reply ONLY in {lang_name}. Never mix languages.
Keep response to 2 sentences. Be warm and focused on safety."""},
                {"role": "user", "content": question}
            ],
            max_tokens=100
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq error: {e}")
        return None

# ── Language Selection ─────────────────────────────────
speak("Welcome to Road Crossing Assistant.", "en")
speak("Please say ONE for English. TWO for Hindi. THREE for Telugu.", "en")

LANG = "en"
for _ in range(4):
    choice = listen(timeout=8, lang="en-IN")
    if choice:
        c = choice.lower()
        if any(x in c for x in ["1", "one", "english"]):
            LANG = "en"
            speak("English selected. I am ready to help you cross the road safely.", "en")
            break
        elif any(x in c for x in ["2", "two", "hindi"]):
            LANG = "hi"
            speak("Hindi selected.", "en")
            speak("मैं तैयार हूँ। आप मुझसे कुछ भी पूछ सकते हैं।", "hi")
            break
        elif any(x in c for x in ["3", "three", "telugu"]):
            LANG = "te"
            speak("Telugu selected.", "en")
            speak("నేను సిద్ధంగా ఉన్నాను. మీరు నన్ను ఏదైనా అడగవచ్చు.", "te")
            break
        else:
            speak("Please say ONE TWO or THREE.", "en")
    else:
        speak("I did not hear you. Please try again.", "en")

SR_LANG = {"en": "en-IN", "hi": "hi-IN", "te": "te-IN"}

# ── YOLO Setup ─────────────────────────────────────────
model = YOLO("best_v4a.pt")

LARGE_VEHICLES = ["truck", "bus"]
SMALL_VEHICLES = ["motorcycle", "bicycle"]
CARS           = ["car"]
ROAD_CLASSES   = ["traffic light", "stop sign", "person"]
ALL_DETECT     = LARGE_VEHICLES + SMALL_VEHICLES + CARS + ROAD_CLASSES

DISPLAY_LABEL = {
    "car":           "Car",
    "truck":         "Large Vehicle",
    "bus":           "Large Vehicle",
    "motorcycle":    "Two Wheeler",
    "bicycle":       "Two Wheeler",
    "person":        "Person",
    "traffic light": "Traffic Light",
    "stop sign":     "Stop Sign",
}

GROUP_COLORS = {
    "Car":           (0, 255, 0),
    "Large Vehicle": (0, 0, 255),
    "Two Wheeler":   (255, 255, 0),
    "Person":        (255, 200, 0),
    "Traffic Light": (0, 255, 255),
    "Stop Sign":     (0, 0, 200),
}

def get_label_and_color(class_name):
    label = DISPLAY_LABEL.get(class_name, class_name)
    color = GROUP_COLORS.get(label, (200, 200, 200))
    return label, color

def detect_traffic_light_color(frame, x1, y1, x2, y2):
    light_region = frame[y1:y2, x1:x2]
    if light_region.size == 0:
        return None
    hsv    = cv2.cvtColor(light_region, cv2.COLOR_BGR2HSV)
    h, w   = light_region.shape[:2]
    top    = hsv[:h//3, :]
    middle = hsv[h//3:2*h//3, :]
    bottom = hsv[2*h//3:, :]

    def count_color(region, lower, upper):
        mask = cv2.inRange(region, lower, upper)
        return cv2.countNonZero(mask)

    red1   = count_color(top,    np.array([0,   100, 100]), np.array([10,  255, 255]))
    red2   = count_color(top,    np.array([160, 100, 100]), np.array([180, 255, 255]))
    yellow = count_color(middle, np.array([20,  100, 100]), np.array([35,  255, 255]))
    green  = count_color(bottom, np.array([40,  100, 100]), np.array([80,  255, 255]))

    max_val = max(red1 + red2, yellow, green)
    if max_val < 10:
        return None
    if red1 + red2 == max_val:
        return "red"
    if yellow == max_val:
        return "yellow"
    return "green"

# ── Shared State ───────────────────────────────────────
current_scene = "Road scene being analyzed"
scene_lock    = threading.Lock()
running       = True

# ── Camera Thread ──────────────────────────────────────
def camera_loop():
    global current_scene, running
    cap = cv2.VideoCapture(r"C:\Users\Hari Aditya\OneDrive\Desktop\traffic_video.mp4")

    while running:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        results = model(frame, verbose=False)

        vehicles            = []
        vehicle_count       = 0
        traffic_light_color = None

        for result in results:
            for box in result.boxes:
                class_id   = int(box.cls[0])
                class_name = model.names[class_id]
                confidence = float(box.conf[0])

                if class_name in ALL_DETECT and confidence > 0.4:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    label, color    = get_label_and_color(class_name)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    display = f"{label} {confidence:.0%}"
                    (tw, th), _ = cv2.getTextSize(display, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                    cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw + 4, y1), color, -1)
                    cv2.putText(frame, display, (x1 + 2, y1 - 4),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

                    if class_name in LARGE_VEHICLES + SMALL_VEHICLES + CARS:
                        vehicles.append(label)
                        vehicle_count += 1

                    if class_name == "traffic light" and confidence > 0.5:
                        tl = detect_traffic_light_color(frame, x1, y1, x2, y2)
                        if tl:
                            traffic_light_color = tl

        parts = []
        if traffic_light_color:
            parts.append(f"Traffic light is {traffic_light_color}")
        if vehicle_count > 0:
            parts.append(f"{vehicle_count} vehicle(s) detected: {', '.join(set(vehicles))}")
        else:
            parts.append("No vehicles detected")

        with scene_lock:
            current_scene = ". ".join(parts)

        cv2.imshow("Road Crossing Assistant", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False
            break

    cap.release()
    cv2.destroyAllWindows()

# Start camera thread
cam_thread = threading.Thread(target=camera_loop, daemon=True)
cam_thread.start()

# ── Main Conversation Loop ─────────────────────────────
speak("I am watching the road. Ask me anything.", "en")

while running:
    question = listen(timeout=8, lang=SR_LANG.get(LANG, "en-IN"))
    if question:
        with scene_lock:
            scene = current_scene
        response = ask_groq(question, scene, LANG)
        if response:
            speak(response, LANG)
    else:
        print("[No input, listening again...]")

speak("Goodbye. Stay safe.", "en")