import time
from asterisk.ami import AMIClient, SimpleAction, EventListener 
import speech_recognition as sr 
import whisper

audio_model = whisper.load_model("base")
model : whisper.Whisper = audio_model
recognizer = sr.Recognizer()
with sr.AudioFile("/home/humanitas/Documents/monitor.wav") as source:
    audio_data = recognizer.record(source)
    try:
        transcript = recognizer.recognize_whisper(audio_data)
        print("Transcription: ", transcript)
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Error fetching result; {e}")

response = model.transcribe("/home/humanitas/Documents/monitor.wav", temperature=0.0, initial_prompt="Do you hear Hello Chronos in the following sentence?", language='en')
print(response)
print(response['text'])
