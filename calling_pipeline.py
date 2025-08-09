import time
import threading
import numpy as np
import sounddevice as sd
from speech_to_text_tester import record_and_transcribe
from llm_response_tester import get_llm_response
from text_to_speech_tester import speak_text, stop_audio

interrupt_flag = threading.Event()

def mic_detects_voice(threshold=0.04, duration=0.15, fs=16000) -> bool:
    try:
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        rms = np.sqrt(np.mean(audio.astype(np.float32) ** 2))
        return rms > threshold
    except Exception as e:
        print(f"[Mic Detection Error] {e}")
        return False

def monitor_for_interrupt(threshold=0.04):
    try:
        while not interrupt_flag.is_set():
            if mic_detects_voice(threshold=threshold):
                stop_audio()
                print("User interrupted the AI.")
                interrupt_flag.set()
                break
            time.sleep(0.05) 
    except Exception as e:
        print(f"[Monitor Error] {e}")

def run_two_way_conversation(api_key: str, wake_words=["exit", "stop", "bye"], duration=5):
    print("\n Voice Agent Started (say 'stop' or 'exit' to quit)\n")

    try:
        while True:
            user_input = record_and_transcribe(duration=duration)
            if not isinstance(user_input, str):
                user_input = ""
            user_input = user_input.strip()

            if not user_input:
                speak_text("Sorry, I didn't catch that. Could you repeat?")
                continue

            print(f"\n You said: {user_input}")

            if any(word in user_input.lower() for word in wake_words):
                speak_text("Okay, ending the conversation. Goodbye.")
                break

            response = get_llm_response(api_key=api_key, speech_to_text_output=user_input)
            if not response:  
                speak_text("I'm sorry, I couldn't generate a response.")
                continue
                
            print(f" AI: {response}")

            interrupt_flag.clear()
            listener_thread = threading.Thread(target=monitor_for_interrupt, daemon=True)
            listener_thread.start()

            speak_text(response)

            listener_thread.join()

    except KeyboardInterrupt:
        stop_audio()
        print("\n[User manually exited]")

