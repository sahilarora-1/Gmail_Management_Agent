# calendar_integration.py

import os
import json
from openai import OpenAI
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# -------------------------------
# OpenAI client setup
# -------------------------------
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not set in environment variables.")

client = OpenAI(api_key=api_key)

# -------------------------------
# Google Calendar API setup
# -------------------------------
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service():
    creds = None
    if os.path.exists("token_calendar.json"):
        creds = Credentials.from_authorized_user_file("token_calendar.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token_calendar.json", "w") as token:
            token.write(creds.to_json())
    service = build("calendar", "v3", credentials=creds)
    return service

# -------------------------------
# Check if slot is free
# -------------------------------
def is_slot_free(service, start_time, end_time):
    """
    Returns True if the time slot is free, False if busy.
    """
    body = {
        "timeMin": start_time,
        "timeMax": end_time,
        "timeZone": "Asia/Kolkata",
        "items": [{"id": "primary"}]
    }
    events_result = service.freebusy().query(body=body).execute()
    busy_times = events_result['calendars']['primary']['busy']
    return len(busy_times) == 0

# -------------------------------
# Add event to calendar
# -------------------------------
def add_event_to_calendar(service, summary, start_time, end_time):
    """
    Add an event to Google Calendar.
    start_time and end_time must be ISO format.
    """
    try:
        event = {
            "summary": summary,
            "start": {"dateTime": start_time, "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end_time, "timeZone": "Asia/Kolkata"},
        }
        created_event = service.events().insert(calendarId="primary", body=event).execute()
        print("\n📅 Calendar Update")
        print("─────────────────────────────")
        print(f"Title      : {summary}")
        print(f"Start Time : {start_time}")
        print(f"End Time   : {end_time}")
        print(f"Event Link : {created_event.get('htmlLink')}")
        print("✅ Calendar updated successfully!\n")
    except Exception as e:
        print(f"❌ Failed to add event: {e}")

# -------------------------------
# Extract event from email using AI
# -------------------------------
def extract_event_from_email(email_body):
    """
    Returns dict: {"title": str, "start_time": str, "end_time": str} in ISO format.
    If no event found, returns None.
    """
    prompt = f"""
    Extract any meeting, appointment, or important date from this email.
    Return ONLY in JSON format like:
    {{
        "title": "<event title>",
        "start_time": "YYYY-MM-DDTHH:MM:SS+05:30",
        "end_time": "YYYY-MM-DDTHH:MM:SS+05:30"
    }}
    If there is no event, return null.
    Email: {email_body}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract events from emails in JSON format only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        content = response.choices[0].message.content.strip()

        if content.lower() in ["null", '"null"']:
            return None

        event_data = json.loads(content)
        if all(k in event_data for k in ["title", "start_time", "end_time"]):
            return event_data
        else:
            print("❌ AI returned invalid event JSON.")
            return None
    except Exception as e:
        print(f"❌ Error extracting event: {e}")
        return None

# -------------------------------
# Process email for calendar
# -------------------------------
def process_email_for_calendar(email_body, email_sender=None, email_subject=None):
    """
    Detect event in email and add to calendar if slot is free.
    Shows email sender/subject for context.
    """
    header_info = ""
    if email_sender or email_subject:
        header_info = "\n"
        if email_sender:
            header_info += f"From    : {email_sender}\n"
        if email_subject:
            header_info += f"Subject : {email_subject}\n"
        print(header_info)

    print("🔹 Processing email for calendar...")
    service = get_calendar_service()
    event = extract_event_from_email(email_body)
    if not event:
        print("ℹ️ No event detected in this email.\n")
        return

    start = event['start_time']
    end = event['end_time']
    if is_slot_free(service, start, end):
        add_event_to_calendar(service, event['title'], start, end)
    else:
        print(f"⚠️ Cannot add '{event['title']}' — slot from {start} to {end} is already booked.\n")
