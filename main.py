import traceback
print("Before import", flush=True)

def main():
    print("Main.py started", flush=True)
    
    try:
        from calling_pipeline import run_two_way_conversation

        print("After import", flush=True)
        print("Starting voice conversation...")
            
        run_two_way_conversation(api_key='')
        
    except ImportError as e:
        print(f"Import Error: {e}", flush=True)
        print("Make sure all dependencies are installed:", flush=True)
        print("pip install openai-whisper sounddevice scipy numpy langchain-groq TTS soundfile python-dotenv", flush=True)
        traceback.print_exc()
    except Exception as e:
        print(f"Unexpected error: {e}", flush=True)
        traceback.print_exc()

if __name__ == "__main__":
    main()