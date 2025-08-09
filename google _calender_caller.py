import re
from google.oauth2 import service_account
from datetime import datetime, timedelta
from googleapiclient.discovery import build

def get_upcoming_calls(service_account_path: str, hours_ahead: int = 24):
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    creds = service_account.Credentials.from_service_account_file(
        service_account_path, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=creds)

    now = datetime.now().isoformat() + 'Z'
    later = (datetime.now() + timedelta(hours=hours_ahead)).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        timeMax=later,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    calls = []

    for event in events:
        start_time = event['start'].get('dateTime', event['start'].get('date'))
        summary = event.get('summary', 'No title')
        description = event.get('description', '')

        
        name_match = re.search(r"Name:\s*(.+)", description)
        number_match = re.search(r"Number:\s*(\+?\d+)", description)

        name = name_match.group(1).strip() if name_match else "Unknown"
        number = number_match.group(1).strip() if number_match else None

        if number:  
            calls.append({
                'name': name,
                'number': number,
                'time': start_time,
                'event_id': event['id'],
                'summary': summary
            })
           
        

    return calls



