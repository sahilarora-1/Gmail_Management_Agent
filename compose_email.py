from openai import OpenAI
import os
import time
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
IGNORE_LIST = [MY_EMAIL, "noreply@gmail.com"]

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
# Generate AI email draft
# ------------------------
def generate_new_email(to_email, subject, instructions, tone="polite and professional"):
    if not instructions.strip():
        instructions = "Please write a concise and professional email."

    prompt = f"""
    You are an AI email assistant.
    Compose an email to {to_email} with subject "{subject}".
    Instructions: {instructions}
    Tone: {tone}.
    Make it concise and professional.
    Do NOT include a greeting like 'Dear ...', subject line, or signature in your response.
    """

    for attempt in range(3):  # retry up to 3 times
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating email (attempt {attempt+1}): {e}")
            time.sleep(2)

    return "Sorry, I couldn't generate the email at this time."

# ------------------------
# Compose email flow
# ------------------------
def compose_email_flow(service, to_email=None, subject=None, instructions=None, tone=None):
    from reply_handler import confirm_and_send  # Local import to prevent circular import

    # Ask inputs if not provided
    if not to_email:
        to_email = input("Recipient email: ").strip()

    # Check ignore list
    if parseaddr(to_email)[1].lower() in [email.lower() for email in IGNORE_LIST]:
        print(f"⚠️ You cannot send an email to yourself or ignored addresses: {to_email}")
        return

    if not subject:
        subject = input("Subject: ").strip()
    subject = subject if subject.strip() else "(No Subject)"

    if not instructions:
        instructions = input("Instructions for AI (optional): ").strip()
    if not tone:
        tone = input("Preferred tone (default polite and professional): ").strip() or "polite and professional"

    # Generate AI draft
    draft = generate_new_email(to_email, subject, instructions, tone)

    # Clean AI draft
    draft_cleaned = clean_ai_draft(draft)

    # ------------------------
    # Add signature
    # ------------------------
    print("\n--- Choose signature info to include ---")
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
    recipient_name = parseaddr(to_email)[0] or "there"

    # Combine greeting + cleaned AI draft + signature
    final_email = f"Dear {recipient_name},\n\n{draft_cleaned}\n\n{signature}"

    # Optional manual edit
    edit_choice = input("\nDo you want to edit the draft before sending? (y/n): ").strip().lower()
    if edit_choice == 'y':
        print("Enter your edited draft (finish with an empty line):")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        final_email = "\n".join(lines)

    # ------------------------
    # Send email
    # ------------------------
    confirm_and_send(service, to_email, subject, final_email)
