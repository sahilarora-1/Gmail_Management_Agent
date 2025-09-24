# main.py
import os
import re
import time
import json
import base64
import socket
from email.mime.text import MIMEText
from email.utils import parseaddr

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Project imports
from spam_classifier import is_spam
from reply_handler import handle_email
from compose_email import compose_email_flow
from calender_integration import process_email_for_calendar
from mass_email import send_mass_email  # Mass email handles AI replies & signatures

# ------------------------
# Config
# ------------------------
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send"
]
REPLIED_FILE = "replied_emails.json"

# ------------------------
# Replied emails tracking
# ------------------------
if os.path.exists(REPLIED_FILE):
    with open(REPLIED_FILE, "r") as f:
        replied_data = json.load(f)
else:
    replied_data = {"replied_ids": []}


def has_replied(email_id: str) -> bool:
    return email_id in replied_data.get("replied_ids", [])


def mark_as_replied(email_id: str):
    if email_id not in replied_data.get("replied_ids", []):
        replied_data.setdefault("replied_ids", []).append(email_id)
        with open(REPLIED_FILE, "w") as f:
            json.dump(replied_data, f, indent=4)


# ------------------------
# Network check
# ------------------------
try:
    socket.create_connection(("gmail.googleapis.com", 443), timeout=10)
    print("Connection successful to Gmail API host.")
except Exception as e:
    print("Connection test failed:", e)


# ------------------------
# Authenticate Gmail
# ------------------------
def authenticate_gmail():
    creds = None
    if os.path.exists("token.json"):
        try:
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        if not creds:
            if not os.path.exists("credentials.json"):
                raise FileNotFoundError("credentials.json not found.")
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    profile = service.users().getProfile(userId="me").execute()
    sender = profile.get("emailAddress")
    return service, sender


# ------------------------
# Helpers
# ------------------------
def decode_base64url(data: str) -> str:
    if not data:
        return ""
    data = data.replace("-", "+").replace("_", "/")
    padding = len(data) % 4
    if padding:
        data += "=" * (4 - padding)
    try:
        return base64.b64decode(data).decode("utf-8", errors="ignore")
    except Exception:
        return ""


def get_message_body(payload: dict) -> str:
    if not payload:
        return ""
    body_text = ""
    mime_type = payload.get("mimeType", "")
    if mime_type == "text/plain" and payload.get("body", {}).get("data"):
        body_text += decode_base64url(payload["body"]["data"])
    for part in payload.get("parts", []) or []:
        body_text += get_message_body(part)
    return body_text


def extract_email_address(from_header: str) -> str:
    if not from_header:
        return ""
    m = re.search(r"<([^>]+)>", from_header)
    if m:
        return m.group(1)
    email_like = re.findall(r"[\w\.-]+@[\w\.-]+", from_header)
    return email_like[0] if email_like else from_header


def safe_fetch(service, msg_id, retries=3):
    for attempt in range(retries):
        try:
            return service.users().messages().get(userId="me", id=msg_id, format="full").execute()
        except Exception:
            time.sleep(2)
    return None


# ------------------------
# Fetch incoming emails
# ------------------------
def fetch_emails(service, n=5):
    try:
        results = service.users().messages().list(
            userId="me", labelIds=["INBOX"], q="is:unread", maxResults=n
        ).execute()
    except Exception:
        return []

    messages = results.get("messages", [])
    emails_list = []

    for msg in messages:
        msg_id = msg.get("id")
        if not msg_id or has_replied(msg_id):
            continue

        msg_data = safe_fetch(service, msg_id)
        if not msg_data:
            continue

        headers = {h["name"]: h["value"] for h in msg_data.get("payload", {}).get("headers", [])}
        subject = headers.get("Subject", "(No Subject)")
        sender_raw = headers.get("From", "(Unknown)")
        sender_email = extract_email_address(sender_raw)
        body = get_message_body(msg_data.get("payload", {})) or "(No content)"

        try:
            if is_spam(body):
                continue
        except Exception:
            pass

        emails_list.append({
            "id": msg_id,
            "sender": sender_email,
            "subject": subject,
            "body": body.strip()
        })

    return emails_list


# ------------------------
# Main loop
# ------------------------
if __name__ == "__main__":
    try:
        service, gmail_sender = authenticate_gmail()
    except Exception as e:
        print("Authentication failed:", e)
        raise SystemExit(1)

    # Load sender info
    try:
        with open("sender_info.json", "r") as f:
            sender_info = json.load(f)
        sender_info["email"] = gmail_sender
    except Exception as e:
        print(f"Failed to load sender_info.json: {e}")
        sender_info = {
            "name": "Sahil Arora",
            "email": gmail_sender,
            "designation": "Team Head",
            "company": "",
            "phone": ""
        }

    print(f"Authenticated as: {gmail_sender}")

    while True:
        print("\n=== AI Gmail Agent ===")
        print("1: Reply to incoming emails")
        print("2: Compose a new email")
        print("3: Send mass email")
        print("4: Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            emails = fetch_emails(service, n=5)
            if not emails:
                print("No emails to process.")
                continue
            for email_data in emails:
                print(f"\n📧 Processing email from {email_data['sender']} with subject: {email_data['subject']}")
                try:
                    handle_email(service, email_data)
                    mark_as_replied(email_data["id"])
                except Exception as e:
                    print(f"Error handling email {email_data['id']}: {e}")
                try:
                    process_email_for_calendar(
                        email_data["body"],
                        email_sender=email_data["sender"],
                        email_subject=email_data["subject"]
                    )
                except Exception as e:
                    print(f"Calendar integration error: {e}")

        elif choice == "2":
            try:
                # Compose single email interactively
                compose_email_flow(service)  # should ask for signature info
            except Exception as e:
                print(f"Error in compose flow: {e}")

        elif choice == "3":
            try:
                # Mass email: signature fetched automatically from sender_info.json
                send_mass_email(service, sender_info)
            except Exception as e:
                print(f"Error running mass email flow: {e}")

        elif choice == "4":
            print("Exiting agent. Goodbye.")
            break

        else:
            print("Invalid choice. Try again.")
