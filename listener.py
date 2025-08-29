# Import libraries
import sounddevice as sd          # For capturing audio from your mic
import json                       # For parsing Vosk's JSON results
from vosk import Model, KaldiRecognizer  # Vosk speech recognition
import sys
import numpy as np
import threading

stop_listening = False  # Flag to tell the callback to stop


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
    if stop_listening:
        raise sd.CallbackStop()  # Stops the stream
    # indata is a numpy array of audio samples
    # Convert float32 to int16 if needed (Vosk expects int16)
    indata_int16 = (indata * 32767).astype('int16') if indata.dtype == 'float32' else indata

    # Feed audio to Vosk
    if rec.AcceptWaveform(indata_int16.tobytes()):
        # True = Vosk has a finalized recognition result
        print(json.loads(rec.Result())["text"])
    else:
        # Partial result while speaking
        print(json.loads(rec.PartialResult())["partial"])

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
            sd.sleep(100)  # sleep 100 ms at a time  # Just a very long sleep; stream ends when callback raises CallbackStop

# Run the listener in a thread so main thread can wait for user input
listener_thread = threading.Thread(target=listen)
listener_thread.start()

input("Press Enter to stop listening...\n")  # Wait for user to type anything
stop_listening = True  # Tell the callback to stop

listener_thread.join()  # Wait for stream to close
print("Stopped listening")