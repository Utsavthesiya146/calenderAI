# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
import uuid
import logging
logging.basicConfig(level=logging.INFO)  # એરર્સ ડીબગ કરવા માટે

app = FastAPI()

# Load service account credentials
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'service_account.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
calendar_service = build('calendar', 'v3', credentials=credentials)

class AppointmentRequest(BaseModel):
    start_time: str
    end_time: str
    summary: str
    attendee_email: str
    timeZone='Asia/Kolkata'

@app.post("/create_event")
async def create_event(request: AppointmentRequest):
    event = {
        'summary': request.summary,
        'start': {
            'dateTime': request.start_time,
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': request.end_time,
            'timeZone': 'UTC',
        },
        'attendees': [{'email': request.attendee_email}],
        'conferenceData': {
            'createRequest': {
                'requestId': str(uuid.uuid4()),
                'conferenceSolutionKey': {'type': 'hangoutsMeet'}
            }
        },
    }
    
    event = calendar_service.events().insert(
        calendarId='9d23676d1e15e9140e9cc944f3ff3355740f76401fa468835d8107fd4a96817d@group.calendar.google.com',
        body=event,
        conferenceDataVersion=1
    ).execute()
    
    return {"event_id": event['id'], "meet_link": event['hangoutLink']}

@app.get("/check_availability")
async def check_availability(start_time: str, end_time: str):
    # Check for existing events in the time range
    events_result = calendar_service.events().list(
        calendarId='primary',
        timeMin=start_time,
        timeMax=end_time,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    return {"available": len(events) == 0}
