import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
    print("Adjusting for background noise...")
    r.adjust_for_ambient_noise(source, duration=1)
    print("Speak now...")
    audio = r.listen(source, timeout=5)

try:
    text = r.recognize_google(audio)
    print(f"You said: {text}")
except sr.UnknownValueError:
    print("Could not understand audio")
except sr.RequestError:
    print("Could not connect to Google Speech Recognition")