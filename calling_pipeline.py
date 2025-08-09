import time
import threading
import numpy as np
import sounddevice as sd
from speech_to_text_tester import record_and_transcribe
from llm_response_tester import get_llm_response
from text_to_speech_tester import speak_text, stop_audio, is_audio_playing

interrupt_flag = threading.Event()
conversation_active = threading.Event()
listening_mode = threading.Event()

def mic_detects_voice(threshold=0.03, duration=0.1, fs=16000) -> bool:
    try:
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        rms = np.sqrt(np.mean(audio.astype(np.float32) ** 2))
        return rms > threshold
    except Exception as e:
        print(f"[Mic Detection Error] {e}")
        return False

def monitor_for_interrupt(threshold=0.03):
    try:
        consecutive_detections = 0
        detection_threshold = 2  
        
        while not interrupt_flag.is_set():
            if not is_audio_playing():
                time.sleep(0.02)
                continue
                
            if mic_detects_voice(threshold=threshold, duration=0.08):  
                consecutive_detections += 1
                if consecutive_detections >= detection_threshold:
                    print("\n User interruption detected!")
                    stop_audio()  
                    interrupt_flag.set()
                    listening_mode.set()
                    break
            else:
                consecutive_detections = max(0, consecutive_detections - 1)  
            
            time.sleep(0.02)  
            
    except Exception as e:
        print(f"[Monitor Error] {e}")

def handle_user_interrupt(api_key: str, duration=5):
    try:
        print(" I'm listening to your interruption...")
        
        time.sleep(0.2)
        
        user_input = record_and_transcribe(duration=duration)
        if not isinstance(user_input, str):
            user_input = ""
        user_input = user_input.strip()
        
        if user_input:
            print(f"\n You said: {user_input}")
            
            if any(word in user_input.lower() for word in ["exit", "stop", "bye", "goodbye"]):
                speak_text("Okay, ending the conversation. Goodbye!")
                return "exit"
            
            print("Processing your input...")
            response = get_llm_response(api_key=api_key, speech_to_text_output=user_input)
            
            if response:
                print(f" AI: {response}")
                
                interrupt_flag.clear()
                listening_mode.clear()
                
                listener_thread = threading.Thread(target=monitor_for_interrupt, daemon=True)
                listener_thread.start()
                
                speak_text(response)
                
            else:
                speak_text("I'm sorry, I couldn't generate a response.")
        
        else:
            print("No input detected after interruption.")
            speak_text("I didn't catch that. Please continue.")
            
        return "continue"
        
    except Exception as e:
        print(f"[Interrupt Handler Error] {e}")
        return "continue"

def run_two_way_conversation(api_key: str, wake_words=["exit", "stop", "bye"], duration=5):
    print("\n  Voice Agent Started (say 'stop' or 'exit' to quit)")
    print(" High-sensitivity interruption enabled - speak anytime to interrupt!")
    print(" Fast response mode activated\n")
    
    conversation_active.set()
    
    try:
        while conversation_active.is_set():
            if listening_mode.is_set():
                result = handle_user_interrupt(api_key, duration)
                if result == "exit":
                    break
                continue
            
            print(" Listening...")
            user_input = record_and_transcribe(duration=duration)
            
            if not isinstance(user_input, str):
                user_input = ""
            user_input = user_input.strip()

            if not user_input:
                speak_text("Sorry, I didn't catch that. Could you repeat?")
                continue

            print(f"\n You said: {user_input}")

            if any(word in user_input.lower() for word in wake_words):
                speak_text("Okay, ending the conversation. Goodbye!")
                break

            print(" Generating response...")
            response = get_llm_response(api_key=api_key, speech_to_text_output=user_input)
            
            if not response:  
                speak_text("I'm sorry, I couldn't generate a response.")
                continue
                
            print(f" AI: {response}")

            interrupt_flag.clear()
            listener_thread = threading.Thread(target=monitor_for_interrupt, daemon=True)
            listener_thread.start()

            speak_text(response)
            
            while is_audio_playing() and not interrupt_flag.is_set():
                time.sleep(0.01) 
            
            if interrupt_flag.is_set():
                listening_mode.set()

    except KeyboardInterrupt:
        print("\n[User manually exited with Ctrl+C]")
        stop_audio()
        conversation_active.clear()
    except Exception as e:
        print(f"\n[Conversation Error] {e}")
        stop_audio()
        conversation_active.clear()
    finally:
        conversation_active.clear()
        interrupt_flag.clear()
        listening_mode.clear()
        stop_audio()
        print(" Voice agent stopped.")

def stop_conversation():
    conversation_active.clear()
    interrupt_flag.set()
    stop_audio()

def is_conversation_active() -> bool:
    return conversation_active.is_set()