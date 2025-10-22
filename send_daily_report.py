import os
import glob
import base64
import pandas as pd
import schedule
import threading
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from PyPDF2 import PdfReader
from openai import OpenAI

# === CONFIGURATION ===
REPORTS_FOLDER = r"C:\RetailEye\outputs"
RECIPIENTS_CSV = r"C:\Users\DELL\Documents\Stores\recipients.csv"
EMAIL_COLUMN = "email"

# Initialize OpenAI client (API key already in environment)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === FUNCTION TO GET NEWEST PDF ===
def get_latest_pdf():
    pdfs = glob.glob(os.path.join(REPORTS_FOLDER, "*.pdf"))
    if not pdfs:
        return None
    return max(pdfs, key=os.path.getctime)

# === FUNCTION TO LOAD RECIPIENTS ===
def load_recipients(csv_path):
    if not os.path.exists(csv_path):
        print(f"⚠️ Recipients CSV not found at {csv_path}")
        return []
    df = pd.read_csv(csv_path)
    if EMAIL_COLUMN not in df.columns:
        print(f"⚠️ Column '{EMAIL_COLUMN}' not found in recipients CSV.")
        return []
    return df[EMAIL_COLUMN].dropna().tolist()

# === FUNCTION TO EXTRACT TEXT FROM PDF ===
def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
        # Truncate to avoid overloading GPT
        return text[:4000].strip()
    except Exception as e:
        print(f"⚠️ Failed to read PDF: {e}")
        return ""

# === FUNCTION TO EXTRACT STORE NAME FROM PDF FILE NAME ===
def extract_store_name(file_path):
    base = os.path.basename(file_path)
    name_part = os.path.splitext(base)[0]
    clean_name = ''.join([c if c.isalnum() or c == ' ' else ' ' for c in name_part]).split()[0]
    return clean_name or "Retail Store"

# === FUNCTION TO GENERATE EMAIL BODY USING OPENAI ===
def generate_email_body(store_name, pdf_path):
    pdf_text = extract_text_from_pdf(pdf_path)
    prompt = f"""
    You are a helpful AI assistant writing daily business summary emails.
    The following is report data for the store "{store_name}".

    ---
    {pdf_text}
    ---

    Highlight key sales trends, performance metrics, or alerts if visible.
    - Include a section titled 'Report:' summarizing the store's performance.
    - Include a section titled 'Suggestions:' providing actionable recommendations to improve sales performance.
    - Do NOT use Markdown or formatting characters (like *, **, #).
    - Keep formatting clean with clear newlines between sections.
    - Do NOT include any personal signature; just end with a polite closing such as 'Best regards' or 'Thank you'.
    - Keep it plain text, not formatted for HTML or Markdown.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional business communication assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ OpenAI generation failed: {e}")
        return f"Hello,\n\nThe daily report for {store_name} has been generated. Please find it attached or view it in the RetailEye app.\n\nBest regards,\nAI Agent"

# === MAIN REPORT SENDER FUNCTION ===
def send_daily_report(service, sender):
    latest_pdf = get_latest_pdf()
    if not latest_pdf:
        print("⚠️ No PDF report found in outputs folder.")
        return

    recipients = load_recipients(RECIPIENTS_CSV)
    if not recipients:
        print("⚠️ No recipients found in CSV.")
        return

    store_name = extract_store_name(latest_pdf)
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")
    subject = f"Daily Report of Store {store_name}"
    body_text = generate_email_body(store_name, latest_pdf)

    message = MIMEMultipart()
    message["to"] = ", ".join(recipients)
    message["from"] = sender
    message["subject"] = subject
    message.attach(MIMEText(body_text))

    # Attach the PDF file
    with open(latest_pdf, "rb") as f:
        part = MIMEBase("application", "pdf")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(latest_pdf)}"')
        message.attach(part)

    raw_message = {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}

    try:
        service.users().messages().send(userId="me", body=raw_message).execute()
        print(f"✅ Smart AI-generated report email for '{store_name}' sent successfully to {len(recipients)} recipients at {now}.")
    except Exception as e:
        print("❌ Error sending daily report:", e)

# === DAILY SCHEDULER FUNCTION ===
def schedule_daily_report(service, sender):
    schedule.every().day.at("20:00").do(send_daily_report, service, sender)

    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(30)

    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    print("🕒 Daily report scheduler started (auto send at 8 PM).")
