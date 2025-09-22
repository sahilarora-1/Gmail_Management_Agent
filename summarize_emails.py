# summarize_emails.py

import os
from openai import OpenAI


# Setup OpenAI client

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not set in environment variables.")

client = OpenAI(api_key=api_key)


# Summarize an email

def summarize_email(email_body):
    """
    Generate a concise 3-bullet summary of an email using OpenAI.
    Returns a string containing the summary.
    """
    prompt = f"Summarize the following email into 3 key bullet points:\n\n{email_body}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You summarize emails in exactly 3 bullet points."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error summarizing email: {e}")
        return "Summary not available."
