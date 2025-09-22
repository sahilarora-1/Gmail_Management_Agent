from openai import OpenAI
import os
import base64
from email.utils import parseaddr
from info_of_sender import choose_signature  # Import signature logic

# ------------------------
# Setup OpenAI client
# ------------------------
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

client = OpenAI(api_key=api_key)

# ------------------------
# Prevent sending emails to yourself
# ------------------------
MY_EMAIL = "your_email@gmail.com"  # Replace with your email
IGNORE_LIST = [MY_EMAIL.lower(), "noreply@gmail.com"]

def normalize_email(email):
    """Normalize email by removing aliases."""
    return email.split('+')[0].lower()

# ------------------------
# Clean AI-generated draft
# ------------------------
def clean_ai_draft(draft):
    """
    Removes greetings, subject lines, and AI-generated signatures from draft.
    """
    lines = draft.splitlines()
    cleaned = []

    for line in lines:
        line_strip = line.strip()
        if not line_strip:
            continue
        # Skip AI-generated greetings
        if line_strip.lower().startswith("dear "):
            continue
        # Skip AI-generated subject lines
        if line_strip.lower().startswith("subject:"):
            continue
        # Skip AI-generated signatures
        if line_strip.lower() in ["best regards,", "regards,", "sincerely,", "thank you,"]:
            continue
        cleaned.append(line_strip)

    return "\n".join(cleaned)

# ------------------------
# Generate AI Summary + Reply
# ------------------------
def generate_summary_and_reply(email_body, sender, subject):
    prompt = f"""
You are an AI email assistant.

1. First, summarize the incoming email in 2-3 sentences.
2. Then, draft a polite and professional reply based on that summary.

Incoming Email:
From: {sender}
Subject: {subject}
Body: {email_body}

Do NOT include a greeting like 'Dear ...', subject line, or signature in your response.
Return your response in this format:

Summary:
[summary here]

Reply:
[reply here]
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        draft = response.choices[0].message.content.strip()
        return draft
    except Exception as e:
        print(f"❌ Error generating reply: {e}")
        return None

# ------------------------
# Send email
# ------------------------
def confirm_and_send(service, to_email, subject, body):
    from email.mime.text import MIMEText

    msg = MIMEText(body)
    msg["to"] = to_email
    msg["subject"] = "Re: " + (subject if subject.strip() else "(No Subject)")

    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    try:
        message = {"raw": raw_message}
        sent = service.users().messages().send(userId="me", body=message).execute()
        print(f"📧 Email sent successfully! ID: {sent['id']}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# ------------------------
# Handle incoming email
# ------------------------
def handle_email(service, email_data):
    sender = email_data["sender"]
    sender_email = parseaddr(sender)[1].lower()

    # Skip emails from yourself or ignored addresses
    if normalize_email(sender_email) in [normalize_email(e) for e in IGNORE_LIST]:
        print(f"⚠️ Skipping email from yourself or ignored sender: {sender_email}")
        return

    subject = email_data["subject"] if email_data["subject"].strip() else "(No Subject)"
    body = email_data["body"]

    print("\n--- Incoming Email ---")
    print(f"From: {sender}")
    print(f"Subject: {subject}")
    print(body[:300] + "..." if len(body) > 300 else body)
    print("----------------------")

    # Generate AI summary + reply
    draft = generate_summary_and_reply(body, sender, subject)
    if not draft:
        print("❌ Failed to generate reply.")
        return

    # Split summary and reply from AI output
    summary, reply = None, None
    if "Summary:" in draft and "Reply:" in draft:
        try:
            parts = draft.split("Reply:")
            summary = parts[0].replace("Summary:", "").strip()
            reply = parts[1].strip()
        except Exception:
            reply = draft
    else:
        reply = draft

    # Clean AI reply
    reply_cleaned = clean_ai_draft(reply)

    print("\n--- AI-generated Summary ---")
    if summary:
        print(summary)
    else:
        print("No summary generated.")
    print("--------------------------")

    print("\n--- AI-generated Reply ---")
    print(reply_cleaned)
    print("--------------------------")

    # Add user signature
    signature_template = choose_signature()  # May contain placeholders {name}, {position}, {contact}
    signature_info = {
        "name": "Sahil Arora",
        "position": "Team Head",
        "contact": "sahil@example.com"
    }
    signature = signature_template.format(
        name=signature_info["name"],
        position=signature_info["position"],
        contact=signature_info["contact"]
    )

    # Extract recipient name
    recipient_name = parseaddr(sender)[0] or "there"

    # Combine greeting + AI reply + signature
    final_reply = f"Dear {recipient_name},\n\n{reply_cleaned}\n\n{signature}"

    print("\n--- Final Email Preview ---")
    print(final_reply)
    print("--------------------------")

    # Confirm before sending
    choice = input("Do you want to send this reply? (y/n): ").strip().lower()
    if choice == "y":
        confirm_and_send(service, sender_email, subject, final_reply)
    else:
        print("❌ Reply discarded.")
