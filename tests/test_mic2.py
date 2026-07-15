import speech_recognition as sr

r = sr.Recognizer()
r.energy_threshold = 50
r.dynamic_energy_threshold = False
r.pause_threshold = 0.5

print("Starting microphone...")
with sr.Microphone() as source:
    print("Microphone ready. Speak now - say ONE")
    import time
    time.sleep(1)
    audio = r.listen(source, timeout=10, phrase_time_limit=5)

print("Processing...")
try:
    text = r.recognize_google(audio)
    print(f"You said: {text}")
except sr.UnknownValueError:
    print("Could not understand")
except sr.RequestError as e:
    print(f"API error: {e}")