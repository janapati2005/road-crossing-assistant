import pyttsx3
import time

def speak(text):
    engine = pyttsx3.init('sapi5')
    engine.setProperty('rate', 145)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()
    engine.stop()

print("Test 1")
speak("Welcome to Road Crossing Assistant")
time.sleep(0.3)

print("Test 2")
speak("Please say ONE for English TWO for Hindi THREE for Telugu")
time.sleep(0.3)

print("Test 3")
speak("English selected. I am ready to help.")
time.sleep(0.3)

print("All done")