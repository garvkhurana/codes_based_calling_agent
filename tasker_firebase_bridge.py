import firebase_admin
from firebase_admin import credentials, db
import time
import json
from datetime import datetime

class TaskerFirebaseBridge:
    def __init__(self, credentials_path: str, database_url: str):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': database_url
                })
                print(" Firebase initialized for Tasker bridge")
            
        except Exception as e:
            print(f" Firebase initialization error: {e}")
            raise
    
    def send_tasker_call_command(self, number: str, caller_name: str, reason: str):
        try:
            ref = db.reference("tasker_commands")
            
            
            tasker_command = {
                "action": "MAKE_CALL",
                "phone_number": number,
                "caller_name": caller_name,
                "call_reason": reason,
                "trigger": True,
                "timestamp": int(time.time()),
                "status": "pending",
                "datetime_readable": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            ref.set(tasker_command)
            
            print(f" Tasker call command sent:")
            print(f" Name: {caller_name}")
            print(f" Number: {number}")
            print(f" Reason: {reason}")
            
            return True
            
        except Exception as e:
            print(f" Error sending Tasker command: {e}")
            return False
    
    def wait_for_call_status(self, timeout_seconds=30):
        print(" Waiting for Tasker to initiate call...")
        
        start_time = time.time()
        ref = db.reference("tasker_commands/status")
        
        while (time.time() - start_time) < timeout_seconds:
            try:
                status = ref.get()
                if status == "calling":
                    print(" Tasker is making the call...")
                    return "calling"
                elif status == "connected":
                    print(" Call connected! Starting AI conversation...")
                    return "connected"
                elif status == "failed":
                    print(" Call failed")
                    return "failed"
                
                time.sleep(2)  
                
            except Exception as e:
                print(f"Error checking status: {e}")
                time.sleep(2)
        
        print(" Timeout waiting for call status")
        return "timeout"
    
    def clear_tasker_command(self):
        try:
            ref = db.reference("tasker_commands")
            ref.update({
                "trigger": False,
                "status": "cleared",
                "timestamp": int(time.time())
            })
            print("🧹 Tasker command cleared")
        except Exception as e:
            print(f" Error clearing command: {e}")
    
    def get_current_command(self):
        try:
            ref = db.reference("tasker_commands")
            return ref.get()
        except Exception as e:
            print(f" Error getting command: {e}")
            return None

tasker_bridge = None

def initialize_tasker_bridge(credentials_path=None, database_url=None):
    global tasker_bridge
    
    if credentials_path is None:
        credentials_path = "calling-agent-293ba-firebase-adminsdk-fbsvc-bff7ff9562.json"
    
    if database_url is None:
        database_url = 'https://calling-agent-adb57-default-rtdb.firebaseio.com/'
    
    tasker_bridge = TaskerFirebaseBridge(credentials_path, database_url)
    return tasker_bridge

def send_call_to_tasker(number: str, caller_name: str, reason: str):
    global tasker_bridge
    if tasker_bridge is None:
        initialize_tasker_bridge()
    
    return tasker_bridge.send_tasker_call_command(number, caller_name, reason)

def wait_for_tasker_call(timeout=30):
    global tasker_bridge
    if tasker_bridge is None:
        initialize_tasker_bridge()
    
    return tasker_bridge.wait_for_call_status(timeout)

def clear_tasker_command():
    global tasker_bridge
    if tasker_bridge is None:
        initialize_tasker_bridge()
    
    tasker_bridge.clear_tasker_command()

def test_tasker_integration():
    print(" Testing Tasker Firebase integration...")
    
    try:
        initialize_tasker_bridge()
        
        success = send_call_to_tasker(
            number="9876543210",
            caller_name="Test Contact",
            reason="Testing Tasker automation"
        )
        
        if success:
            print(" Test command sent to Firebase")
            print(" Now check your Tasker app on Android phone")
            print(" Waiting for Tasker response...")
            
            status = wait_for_tasker_call(timeout=60)
            print(f"Final status: {status}")
            
            input("Press Enter to clear the command...")
            clear_tasker_command()
            
        else:
            print(" Failed to send test command")
    
    except Exception as e:
        print(f" Test error: {e}")

if __name__ == "__main__":
    test_tasker_integration()