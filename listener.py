# Import libraries
import sounddevice as sd          # For capturing audio from your mic
import json                       # For parsing Vosk's JSON results
from vosk import Model, KaldiRecognizer  # Vosk speech recognition
import sys

# Sampling rate — common mic rates are 16000 or 44100 Hz
SAMPLE_RATE = 16000

# Load Vosk model
model = Model("C:/Users/rieli/OneDrive/Desktop/project/pythonappforlistening/models/vosk-model-en-us-0.22")

# Create recognizer object with the model and sample rate
rec = KaldiRecognizer(model, SAMPLE_RATE)

# Choose your microphone device index (from sd.query_devices())
DEVICE_INDEX = 2  # replace with your mic index

# This function is called automatically for each chunk of audio
def callback(indata, frames, time, status):
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

# Open input stream from your mic
with sd.InputStream(
        samplerate=SAMPLE_RATE,
        device=DEVICE_INDEX,
        channels=1,         # Mono mic
        dtype='int16',      # Matches Vosk requirement
        blocksize=8000,     # Number of samples per chunk
        callback=callback):   # Function to process each chunk
    
    print("Listening to microphone...")
    sd.sleep(60000)  # Listen for 60 seconds
