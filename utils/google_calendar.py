import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# Load credentials from environment or file
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_CREDENTIALS_PATH', 'google-calendar-creds.json')
CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID', 'primary')  # Use 'primary' for default calendar

def get_calendar_service():
    """Authenticate and return Google Calendar service"""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=['https://www.googleapis.com/auth/calendar']
    )
    return build('calendar', 'v3', credentials=credentials)

def create_event(serviceman_email, request_details):
    """Create a calendar event for a service appointment"""
    service = get_calendar_service()
    
    event = {
        'summary': f"Service: {request_details['category']}",
        'description': request_details['description'],
        'start': {
            'dateTime': f"{request_details['date']}T{request_details['start_time']}:00",
            'timeZone': 'Asia/Kolkata',  # Change to your timezone
        },
        'end': {
            'dateTime': f"{request_details['date']}T{request_details['end_time']}:00",
            'timeZone': 'Asia/Kolkata',
        },
        'attendees': [{'email': serviceman_email}],
        'reminders': {
            'useDefault': True,
        },
    }
    
    return service.events().insert(
        calendarId=CALENDAR_ID,
        body=event
    ).execute()

def get_available_slots(serviceman_email, date):
    """Get busy slots for a serviceman on a given date"""
    service = get_calendar_service()
    
    # Convert date to datetime range
    start = f"{date}T00:00:00"
    end = f"{date}T23:59:59"
    
    freebusy = service.freebusy().query(body={
        "timeMin": start,
        "timeMax": end,
        "items": [{"id": serviceman_email}]
    }).execute()
    
    return freebusy['calendars'][serviceman_email]['busy']