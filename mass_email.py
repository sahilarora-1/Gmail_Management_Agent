# mass_email.py
import csv
import re
import time
import base64
from email.mime.text import MIMEText
from reply_handler import generate_ai_reply_for_mass  # Updated AI function for mass emails

# ------------------------
# Config
# ------------------------
RATE_LIMIT_SECONDS = 1  # delay between sending emails

# ------------------------
# Helpers
# ------------------------
def is_valid_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def _read_recipients_from_csv(filename: str):
    """Return list of dicts: [{'name': ..., 'email': ...}, ...]"""
    recipients = []
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) < 2:
                    continue
                name = row[0].strip()
                email = row[1].strip()
                if not is_valid_email(email):
                    continue
                recipients.append({"name": name, "email": email})
    except FileNotFoundError:
        print(f"CSV file not found: {filename}")
    return recipients

# ------------------------
# Mass email flow
# ------------------------
def send_mass_email(service, sender_info):
    """
    Sends personalized AI-generated emails to multiple recipients.
    Signatures are automatically taken from sender_info.json.
    Prompts user for specifications instead of using a fixed template.
    """
    choice = input("Send emails (1) manually enter or (2) load from CSV? ").strip()
    recipients = []

    if choice == '1':
        raw_emails = input("Enter emails separated by commas: ").strip()
        for e in raw_emails.split(','):
            e = e.strip()
            if is_valid_email(e):
                recipients.append({"name": e.split('@')[0].capitalize(), "email": e})
    elif choice == '2':
        fname = input("CSV filename (default emails.csv): ").strip() or 'emails.csv'
        recipients = _read_recipients_from_csv(fname)
    else:
        print("Invalid choice. Aborting.")
        return

    if not recipients:
        print("No valid recipient emails found. Aborting.")
        return

    subject = input("Subject: ").strip()
    print("Enter any special instructions or specifications for the AI (tone, style, points to mention). Leave blank for default tone.")
    instructions = input("Instructions: ").strip()

    # ------------------------
    # Preview first 3 recipients
    # ------------------------
    print("\n--- Preview (first 3 recipients) ---")
    for r in recipients[:3]:
        ai_body = generate_ai_reply_for_mass(
            recipient_name=r['name'],
            instructions=instructions,
            subject=subject
        )
        signature = f"\n\n{sender_info['name']}\n{sender_info.get('designation','')}\n{sender_info.get('company','')}\n{sender_info.get('phone','')}".strip()
        print(f"To: {r['email']}\nSubject: {subject}\nBody:\n{ai_body}{signature}\n---\n")

    confirm = input(f"Proceed to send to {len(recipients)} recipients? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled by user.")
        return

    # ------------------------
    # Send emails
    # ------------------------
    for r in recipients:
        ai_body = generate_ai_reply_for_mass(
            recipient_name=r['name'],
            instructions=instructions,
            subject=subject
        )
        signature = f"\n\n{sender_info['name']}\n{sender_info.get('designation','')}\n{sender_info.get('company','')}\n{sender_info.get('phone','')}".strip()
        final_body = ai_body + signature  # append signature only once

        msg = MIMEText(final_body)
        msg["to"] = r["email"]
        msg["from"] = sender_info["email"]
        msg["subject"] = subject

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        try:
            service.users().messages().send(userId='me', body={'raw': raw}).execute()
            print(f"✅ Sent to {r['name']} <{r['email']}>")
        except Exception as e:
            print(f"❌ Error sending to {r['email']}: {e}")
        time.sleep(RATE_LIMIT_SECONDS)
