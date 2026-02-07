import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # This requires credentials.json to be in the root folder
            if not os.path.exists('credentials.json'):
                print("❌ ERROR: credentials.json not found.")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

# Global configuration
HOST_EMAIL = "sofstzz@gmail.com" # TODO: Move to .env for production

def schedule_event(summary, description="Booked via CallPilot", attendee_email=None):
    """
    Creates an event for 'Tomorrow at 10 AM' (Simple Logic for MVP)
    In a real app, we would parse the specific date/time from the AI.
    """
    service = get_calendar_service()
    if not service:
        return "Error: Calendar unavailable"

    # LOGIC: For this demo, we always book Tomorrow at 10:00 AM
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    start_time = datetime.datetime.combine(tomorrow, datetime.time(10, 0))
    end_time = start_time + datetime.timedelta(hours=1)
    
    event = {
        'summary': summary,
        'location': 'Online',
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Africa/Addis_Ababa',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Africa/Addis_Ababa',
        },
    }

    if attendee_email:
        event['attendees'] = [{'email': attendee_email}]
    
    # Add a hardcoded host/consultant email if configured
    # This ensures "the guy sending the link" also gets an invite/notification
    # even if not the calendar owner.
    if HOST_EMAIL:
        if 'attendees' not in event:
            event['attendees'] = []
        event['attendees'].append({'email': HOST_EMAIL})

    try:
        event_result = service.events().insert(calendarId='primary', body=event).execute()
        return event_result.get('htmlLink')
    except Exception as e:
        print(f"Calendar Error: {e}")
        return None