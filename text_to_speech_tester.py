print("Before imports")
import threading
import os
import pyttsx3
print("After imports")

tts_engine = None
tts_lock = threading.Lock()
is_speaking = threading.Event()
stop_speaking = threading.Event()

def initialize_tts():
    global tts_engine
    if tts_engine is None:
        try:
            print("Initializing pyttsx3 TTS engine...")
            tts_engine = pyttsx3.init()
            
            voices = tts_engine.getProperty('voices')
            if voices:
                tts_engine.setProperty('voice', voices[0].id)
            
            tts_engine.setProperty('rate', 200)  
            tts_engine.setProperty('volume', 0.9)
            
            print(" TTS engine initialized successfully!")
            
        except Exception as e:
            print(f" TTS initialization error: {e}")
            tts_engine = None
    
    return tts_engine

def speak_text_thread(text: str):
    global tts_engine
    try:
        with tts_lock:
            engine = initialize_tts()
            if engine is None:
                print(" TTS engine not available")
                return
            
            is_speaking.set()
            stop_speaking.clear()
            
            sentences = text.split('. ')
            
            for sentence in sentences:
                if stop_speaking.is_set():
                    print("Speech stopped due to interruption")
                    break
                    
                if sentence.strip():
                    sentence = sentence.strip()
                    if not sentence.endswith('.') and sentence != sentences[-1]:
                        sentence += '.'
                    
                    try:
                        engine.say(sentence)
                        engine.runAndWait()
                    except Exception as e:
                        print(f"Speech error: {e}")
                        break
            
    except Exception as e:
        print(f"Speech thread error: {e}")
    finally:
        is_speaking.clear()

def speak_text(text: str):
    try:
        print(f"Speaking: {text}")
        
        stop_audio()
        
        speech_thread = threading.Thread(target=speak_text_thread, args=(text,), daemon=True)
        speech_thread.start()
        
        threading.Timer(0.1, lambda: None).start()
        
    except Exception as e:
        print(f" TTS error: {e}")

def stop_audio():
    global tts_engine
    try:
        stop_speaking.set()
        
        with tts_lock:
            if tts_engine is not None:
                try:
                    tts_engine.stop()
                except:
                    pass  
        
        is_speaking.clear()
        
    except Exception as e:
        print(f"Stop audio error: {e}")

def is_audio_playing() -> bool:
    return is_speaking.is_set() and not stop_speaking.is_set()

def get_tts_status():
    return {
        "is_speaking": is_speaking.is_set(),
        "stop_requested": stop_speaking.is_set(),
        "engine_available": tts_engine is not None
    }


try:
    initialize_tts()
except:
    pass 

print(" pyttsx3 TTS module initialized. Ready to speak!", flush=True)