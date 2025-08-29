# Import libraries
import sounddevice as sd          # For capturing audio from your mic
import json                       # For parsing Vosk's JSON results
from vosk import Model, KaldiRecognizer  # Vosk speech recognition
import sys
import numpy as np
import threading
import keyboard

stop_listening = False  # Flag to tell the callback to stop

pause_listening = False # stop taking data in

latest_text = ""

# Sampling rate — common mic rates are 16000 or 44100 Hz
SAMPLE_RATE = 16000

# Load Vosk model
model = Model("C:/Users/rieli/Desktop/ProgrammingProjects/MachineLearningSpeechRecognition/models/vosk-model-en-us-0.22")

# Create recognizer object with the model and sample rate
rec = KaldiRecognizer(model, SAMPLE_RATE)

# Choose your microphone device index (from sd.query_devices())
source_choice = input("Select audio source (mic/speaker): ").strip().lower()

if source_choice == "mic":
    DEVICE_INDEX = 1  # Replace with your microphone index
    CHANNELS = 1
elif source_choice == "speaker":
    DEVICE_INDEX = 3  # Replace with your loopback/speaker index probably the WASAPI speaker
    CHANNELS = 1
else:
    sys.exit("Invalid choice. Exiting...")

# This function is called automatically for each chunk of audio
def callback(indata, frames, time, status):
    global latest_text # file to give chatgpt
    if stop_listening:
        raise sd.CallbackStop()  # Stops the stream
    if pause_listening:
        return  # skip processing audio while paus
    # indata is a numpy array of audio samples
    # Convert float32 to int16 if needed (Vosk expects int16)
    indata_int16 = (indata * 32767).astype('int16') if indata.dtype == 'float32' else indata

    # Feed audio to Vosk
    if rec.AcceptWaveform(indata_int16.tobytes()):
        # True = Vosk has a finalized recognition result
        #print(json.loads(rec.Result())["text"])
        latest_text = json.loads(rec.Result())["text"]
        print("\nFinalized:", latest_text)  # new line so it’s not overwritten
    else:
        # Partial result while speaking
        #print(json.loads(rec.PartialResult())["partial"])
        latest_text = json.loads(rec.PartialResult())["partial"]
        print(latest_text, end='\r', flush=True)  # overwrite line for real-time partial
    
    

def spacebar_listener():
    global pause_listening
    while not stop_listening:
        if keyboard.is_pressed("space"):
            pause_listening = not pause_listening
            print("\nPaused" if pause_listening else "\nResumed", flush=True)
            while keyboard.is_pressed("space"):
                pass  # wait until key is released to prevent multiple toggles

keyboard_thread = threading.Thread(target=spacebar_listener, daemon=True)
keyboard_thread.start()

def listen():
    # Open input stream from your mic
    with sd.InputStream(
            samplerate=SAMPLE_RATE,
            device=DEVICE_INDEX,
            channels=CHANNELS,        
            dtype='int16',      # Matches Vosk requirement
            blocksize=8000,     # Number of samples per chunk
            callback=callback):   # Function to process each chunk
        
        print("Listening to microphone...")
        while not stop_listening:
            sd.sleep(100)  # sleep 100 ms at a time  
# Run the listener in a thread so main thread can wait for user input
listener_thread = threading.Thread(target=listen)
listener_thread.start()

input("Press Enter to stop listening...\n")  # Wait for user to type anything
stop_listening = True  # Tell the callback to stop

listener_thread.join()  # Wait for stream to close
print("Stopped listening")