📧 AI-Powered Email Agent

An intelligent email assistant that automates inbox management, reply generation, and scheduling. Built to save time and enhance productivity, this agent integrates with Gmail and Google Calendar to give users a seamless communication experience.

🚀 Features

📩 Fetch Unread Emails – Pulls only the latest unread emails from your inbox.

🛡 Spam Detection – Classifies emails as spam or not spam before processing.

📝 Email Summarization – Generates concise summaries of emails for quick review.

🤖 AI Reply Generation – Drafts multiple response options for you to choose from.

✅ User Confirmation – Always asks before sending a reply to avoid mistakes.

✍️ Manual Email Composition – Compose and send emails directly from the agent.

📅 Google Calendar Integration – Auto-books events mentioned in emails, prevents double bookings.

🖊 Custom Signatures – Add your name, role, and signature to outgoing emails.

🔄 Avoids Duplicate Replies – Skips emails that have already been handled.

🔢 Custom Email Fetch Limit – Decide how many emails to process at once.

✨ AI-Powered Email Writing – Provide just the recipient, subject, tone, or special instructions, and let the agent auto-generate professional emails.

📂 Project Structure
📦 email-agent
 ┣ 📜 main_agent.py     # Main script
 ┣ 📜 requirements.txt   # Dependencies
 ┣ 📜 README.md          # Project documentation
 ┗ 📂 credentials        # Google API credentials

⚙️ Setup & Installation

Clone the Repository

git clone https://github.com/your-username/email-agent.git
cd email-agent


Install Dependencies

pip install -r requirements.txt


Set Up Google API Credentials

Enable the Gmail API and Google Calendar API from Google Cloud Console
.

Download your credentials.json file and place it inside the credentials folder.

Run the Agent

python gmail_agent.py

🛠 Usage

When you run the program, you’ll see options like:

1: Reply to incoming emails
2: Compose a new email (manual or AI-generated)
3: Exit


Select 1 to fetch, summarize, and reply to unread emails.

Select 2 to compose a new email manually or let AI generate one for you.

Select 3 to exit the program.

📊 Tech Stack

Python 3

Gmail API

Google Calendar API

Machine Learning (Spam Detection)

AI Text Generation (for replies & email writing)

🌟 Future Enhancements

📎 Add image attachments in emails.

📊 Rank emails by priority/importance.

☁️ Convert into a SaaS platform for broader usage.

🤝 Contributing

Contributions are welcome! Feel free to fork the repo, open issues, or submit PRs.

📜 License

This project is licensed under the MIT License – free to use and modify.

👤 Author

Your Name
