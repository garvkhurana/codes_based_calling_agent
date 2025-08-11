import time
import schedule
import threading
from datetime import datetime, timedelta
from google_calender_caller import get_upcoming_calls
from tasker_firebase_bridge import send_call_to_tasker, wait_for_tasker_call, clear_tasker_command
from calling_pipeline import run_two_way_conversation
import os

class TaskerCallScheduler:
    def __init__(self, service_account_path: str, groq_api_key: str):
        self.service_account_path = service_account_path
        self.groq_api_key = groq_api_key
        self.processed_calls = set()
        self.active_call = False
        
    def check_and_schedule_calls(self):
        try:
            print(" Checking calendar for upcoming calls...")
            
            upcoming_calls = get_upcoming_calls(
                service_account_path=self.service_account_path, 
                hours_ahead=2
            )
            
            if not upcoming_calls:
                print("No upcoming calls found.")
                return
                
            print(f" Found {len(upcoming_calls)} upcoming calls")
            
            for call in upcoming_calls:
                call_id = call['event_id']
                
                if call_id in self.processed_calls:
                    continue
                    
                call_time = datetime.fromisoformat(call['time'].replace('Z', '+00:00'))
                current_time = datetime.now(call_time.tzinfo)
                
                time_diff = (call_time - current_time).total_seconds()
                
                if -300 <= time_diff <= 300:  
                    print(f"Time to call {call['name']} ({call['number']})")
                    self.initiate_tasker_call(call)
                    self.processed_calls.add(call_id)
                elif time_diff > 0:
                    minutes_remaining = int(time_diff/60)
                    print(f" Call to {call['name']} in {minutes_remaining} minutes")
                    
        except Exception as e:
            print(f" Error checking calls: {e}")
    
    def initiate_tasker_call(self, call_info):
        try:
            if self.active_call:
                print(" Another call is already active. Skipping.")
                return
                
            self.active_call = True
            
            print(f"\n Triggering Tasker to call {call_info['name']}")
            print(f" Number: {call_info['number']}")
            print(f" Reason: {call_info['reason']}")
            
            success = send_call_to_tasker(
                number=call_info['number'],
                caller_name=call_info['name'],
                reason=call_info['reason']
            )
            
            if not success:
                print("Failed to send command to Tasker")
                self.active_call = False
                return
            
            print("Command sent to Tasker!")
            print(" Check your phone - Tasker should be making the call...")
            
            call_status = wait_for_tasker_call(timeout=45)
            
            if call_status == "connected":
                print(" Call connected! Starting AI conversation in 3 seconds...")
                time.sleep(3) 
                
                self.start_ai_conversation_for_call(call_info)
                
            elif call_status == "calling":
                print(" Call is being made. Starting AI conversation...")
                time.sleep(5)
                self.start_ai_conversation_for_call(call_info)
                
            else:
                print(f"Call failed or timed out. Status: {call_status}")
                
            clear_tasker_command()
            
        except Exception as e:
            print(f" Error in Tasker call initiation: {e}")
        finally:
            self.active_call = False
    
    def start_ai_conversation_for_call(self, call_info):
        try:
            print(f"\n Starting AI conversation for call with {call_info['name']}")
            print(f" Call context: {call_info['reason']}")
            print(" AI is now ready to talk...")
            print(" Make sure your laptop audio is connected to phone!")
            
            run_two_way_conversation(api_key=self.groq_api_key, duration=5)
            
        except Exception as e:
            print(f"Error in AI conversation: {e}")
        finally:
            print(f"\n Call with {call_info['name']} completed")
    
    def start_monitoring(self):
        print(" Starting Tasker Call Scheduler...")
        print(" Make sure Tasker is running on your Android phone!")
        print(" Firebase connection established")
        print(" Calendar monitoring active\n")
        
        schedule.every(1).minutes.do(self.check_and_schedule_calls)
        
        self.check_and_schedule_calls()
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(30)  
            except KeyboardInterrupt:
                print("\n Scheduler stopped by user")
                break
            except Exception as e:
                print(f" Scheduler error: {e}")
                time.sleep(30)

def main():    
    print(" AI Calling Agent with Tasker Integration")
    print("=" * 50)
    
    SERVICE_ACCOUNT_PATH = "callingagent-468309-db3b5c8cd80d.json"
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    
    if not GROQ_API_KEY:
        print(" No GROQ_API_KEY found in environment")
        GROQ_API_KEY = input("Enter your Groq API key: ").strip()
        
        if not GROQ_API_KEY:
            print(" No API key provided. Exiting...")
            return
    
    print("\n Setup Checklist:")
    print("✓ Tasker app installed on Android phone")
    print("✓ Phone connected to same WiFi as laptop")
    print("✓ Tasker profile created to monitor Firebase")
    print("✓ Phone audio connected to laptop (Bluetooth/AUX)")
    print("✓ Calendar events created with contact info")
    
    input("\nPress Enter when setup is complete...")
    
    scheduler = TaskerCallScheduler(SERVICE_ACCOUNT_PATH, GROQ_API_KEY)
    
    try:
        scheduler.start_monitoring()
    except KeyboardInterrupt:
        print("\n Scheduler stopped")
    except Exception as e:
        print(f" Error: {e}")

if __name__ == "__main__":
    main()