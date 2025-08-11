import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate(r"C:\Users\garvk\OneDrive - Bhagwan Parshuram Institute of Technology\Desktop\advance_projects\calling_agent\calling-agent-adb57-firebase-adminsdk-fbsvc-d3e0cae176.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://calling-agent-adb57-default-rtdb.firebaseio.com/'
})

def send_call_command(number, message):
    ref = db.reference("call_command")
    ref.set({
        "number": number,
        "message": message,
        "trigger": True
    })


if __name__ == "__main__":
    send_call_command("9876543210", "Hello, this is a test call")
    print('its done')
