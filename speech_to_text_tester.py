import whisper
import sounddevice as sd
from scipy.io.wavfile import write
import tempfile
import os


print("Loading Whisper model (tiny)...")
whisper_model=None

def record_and_transcribe(duration=5, fs=16000) -> str:
    
    try:
        global whisper_model
        if whisper_model is None:
            whisper_model = whisper.load_model("tiny")
        print(f"🎤 Recording for {duration} seconds...")
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()

        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            write(tmp_wav.name, fs, audio)
            temp_path = tmp_wav.name

        print("📝 Transcribing...")
        result = whisper_model.transcribe(temp_path, language="en")
        text = result.get("text", "").strip()

        os.remove(temp_path)

        return text

    except Exception as e:
        print(f"❌ Error in STT: {e}")
        

