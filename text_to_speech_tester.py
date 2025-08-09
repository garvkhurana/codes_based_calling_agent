print("Before imports")
import threading
import os
print("After imports")

OUTPUT_FILE = "output.wav"
playback_thread = None
playback_lock = threading.Lock()
is_playing = threading.Event()
_tts_model = None

def get_tts_model():
    global _tts_model
    if _tts_model is None:
        print("Loading TTS model (this may take a moment)...")
        from TTS.api import TTS

        try:
            _tts_model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
        except:
            # Fallback to VCTK model
            try:
                _tts_model = TTS(model_name="tts_models/en/vctk/vits")
            except Exception as e:
                print(f"TTS model loading failed: {e}")
                raise
    return _tts_model

def generate_tts(text: str):
    """Generate speech from text and save to file."""
    try:
        tts_model = get_tts_model()
        tts_model.tts_to_file(text=text, file_path=OUTPUT_FILE)
    except Exception as e:
        print(f"❌ TTS generation error: {e}")
        raise

def _play_audio():
    """Play audio file in a non-blocking way."""
    try:
        import sounddevice as sd
        import soundfile as sf
        if not os.path.exists(OUTPUT_FILE):
            print("❌ No audio file found.")
            return
            
        data, samplerate = sf.read(OUTPUT_FILE, dtype='float32')
        is_playing.set()
        sd.play(data, samplerate)
        sd.wait()  
        is_playing.clear()
        
    except Exception as e:
        print(f"❌ Playback error: {e}")
        is_playing.clear()

def play_audio():
    import sounddevice as sd
    global playback_thread
    stop_audio()
    
    with playback_lock:
        playback_thread = threading.Thread(target=_play_audio, daemon=True)
        playback_thread.start()

def stop_audio():
    import sounddevice as sd
    is_playing.clear()
    sd.stop()
    
    global playback_thread
    if playback_thread and playback_thread.is_alive():
        playback_thread.join(timeout=0.1)

def speak_text(text: str):
    try:
        print(f" Speaking: {text}")
        stop_audio()
        generate_tts(text)
        play_audio()
    except Exception as e:
        print(f"TTS error: {e}")

print("TTS module initialized. Ready to speak!", flush=True)        

