# gmail_agent.py

import socket
import time
import base64
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from spam_classifier import is_spam
from reply_handler import handle_email
from compose_email import compose_email_flow
from calender_integration import process_email_for_calendar

# ------------------------
# User email (to skip own emails)
# ------------------------
MY_EMAIL = "sahilkca23@gmail.com"  # replace with your Gmail address

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

# ------------------------
# Replied emails tracking
# ------------------------
REPLIED_FILE = "replied_emails.json"
if os.path.exists(REPLIED_FILE):
    with open(REPLIED_FILE, "r") as f:
        replied_data = json.load(f)
else:
    replied_data = {"replied_ids": []}

def has_replied(email_id):
    return email_id in replied_data["replied_ids"]

def mark_as_replied(email_id):
    if email_id not in replied_data["replied_ids"]:
        replied_data["replied_ids"].append(email_id)
        with open(REPLIED_FILE, "w") as f:
            json.dump(replied_data, f, indent=4)

# ------------------------
# Test connectivity
# ------------------------
try:
    socket.create_connection(("gmail.googleapis.com", 443), timeout=10)
    print("Connection successful!")
except Exception as e:
    print("Connection failed:", e)
    exit(1)

# ------------------------
# 1. Authenticate Gmail
# ------------------------
def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('gmail', 'v1', credentials=creds)
    except Exception as e:
        print(f"Failed to build Gmail service: {e}")
        exit(1)
    return service

# ------------------------
# 2. Safe fetch message with retry
# ------------------------
def safe_fetch(service, msg_id, retries=3):
    for attempt in range(retries):
        try:
            return service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
        except HttpError as e:
            print(f"HTTP error: {e}. Retrying in 2s...")
            time.sleep(2)
    return None

# ------------------------
# 3. Fetch incoming emails (skip spam, self, and already replied)
# ------------------------
def fetch_emails(service, n=2):
    try:
        results = service.users().messages().list(
            userId='me',
            maxResults=n,
            fields='messages(id),nextPageToken'
        ).execute()
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []

    messages = results.get('messages', [])
    emails_list = []

    for msg in messages:
        msg_id = msg['id']

        # Skip already replied emails
        if has_replied(msg_id):
            continue

        msg_data = safe_fetch(service, msg_id)
        if not msg_data:
            continue

        # Extract headers
        headers = {h['name']: h['value'] for h in msg_data.get('payload', {}).get('headers', [])}
        subject = headers.get('Subject', '(No Subject)')
        sender = headers.get('From', '(Unknown Sender)')

        # Skip your own sent emails
        if MY_EMAIL.lower() in sender.lower():
            continue

        # Decode body safely
        body = ''
        payload = msg_data.get('payload', {})
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    body += base64.urlsafe_b64decode(part['body']['data'].encode()).decode('utf-8', errors='ignore')
        else:
            if 'body' in payload and 'data' in payload['body']:
                body += base64.urlsafe_b64decode(payload['body']['data'].encode()).decode('utf-8', errors='ignore')

        if not body:
            body = '(No content)'

        # Skip spam
        try:
            if is_spam(body):
                print(f"⚠️ Skipping spam email: {subject}")
                continue
        except Exception as e:
            print(f"Error in spam check: {e}")

        emails_list.append({
            'id': msg_id,
            'sender': sender,
            'subject': subject,
            'body': body.strip()
        })

    return emails_list

# ------------------------
# 4. Main agent loop
# ------------------------
if __name__ == '__main__':
    service = authenticate_gmail()

    while True:
        print("\n=== AI Gmail Agent ===")
        print("1: Reply to incoming emails")
        print("2: Compose a new email")
        print("3: Exit")
        choice = input("Select an option: ").strip()

        if choice == '1':
            emails = fetch_emails(service, n=3)
            if not emails:
                print("No emails to process.")
                continue
            for email_data in emails:
                print(f"\n📧 Processing email from {email_data['sender']} with subject: {email_data['subject']}")

                # Handle email (reply generation etc.)
                handle_email(service, email_data)

                # Mark as replied
                mark_as_replied(email_data['id'])

                # --- Calendar integration: automatically add events ---
                try:
                    process_email_for_calendar(
                        email_data['body'],
                        email_sender=email_data['sender'],
                        email_subject=email_data['subject']
                    )
                except Exception as e:
                    print(f"⚠️ Calendar integration error: {e}")

        elif choice == '2':
            compose_email_flow(service)

        elif choice == '3':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Try again.")
