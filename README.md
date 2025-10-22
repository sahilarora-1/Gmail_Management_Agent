# 📧 AI-Powered Email & Report Automation Agent

An intelligent communication assistant that automates email management, reply generation, report analysis, and daily scheduling — integrating seamlessly with Gmail, Google Calendar, and OpenAI GPT for true hands-free productivity.

Built to help teams and individuals save time, stay organized, and communicate smarter.

# 🚀 Features
✉️ Email Automation

📩 Fetch Unread Emails – Pulls only the latest unread emails from your inbox.

🛡 Spam Detection (ML Model) – Filters spam before processing.

📝 Email Summarization – Generates concise summaries for quick understanding.

🤖 AI Reply Generation – Drafts multiple response options powered by OpenAI.

✅ User Confirmation Flow – Ensures replies are verified before sending.

✍️ Manual Composition – Compose emails manually or use AI-assisted writing.

📤 Mass Emailing – Send personalized bulk emails using a CSV recipient list.

🖊 Custom Signatures – Add your name, designation, and contact info automatically.

🔄 Duplicate Prevention – Skips already replied-to emails.

🔢 Custom Fetch Limit – Choose how many emails to process at once.

📊 AI-Powered Report Emailing (New!)

🧠 PDF Report Reading – Automatically reads the latest generated store report (.pdf).

🧾 AI Summarization of Reports – Extracts text from the PDF and uses OpenAI GPT to write a meaningful, professional summary.

📈 Smart Subject Generation – Automatically names emails like:

“Daily Report of Store Lavish Sup”

📨 Daily Schedule – Automatically sends the report every day at 8 PM, or on-demand via menu option.

💬 Context-Aware Email Writing – GPT reads the actual PDF content and crafts an insightful email mentioning trends, performance, and next actions.

🔗 RetailEye App Integration – Adds a professional note guiding users to check the detailed report or view analytics in the RetailEye app.

📅 Calendar Integration

⏰ Event Detection – Scans incoming emails for date/time mentions.

📆 Auto-Booking – Automatically schedules events in Google Calendar.

🚫 Conflict Prevention – Detects and avoids double-booking the same time slots.


# ⚙️ Setup & Installation


# 1️⃣ Clone the Repository
git clone https://github.com/sahilarora-1/Gmail_Management_Agent.git
cd Gmail_Management_Agent

# 2️⃣ Install Dependencies
pip install -r requirements.txt


(Make sure the following are installed in requirements.txt:)
google-auth, google-auth-oauthlib, google-api-python-client, openai, pypdf, schedule, pandas

# 3️⃣ Set Up Google APIs

Enable the Gmail API and Google Calendar API from your Google Cloud Console.

Download your credentials.json and place it inside the project folder.

On first run, a browser window will open for authentication and create a token.json.

# 4️⃣ Add Your OpenAI API Key

Set your OpenAI key as an environment variable (PowerShell):

setx OPENAI_API_KEY "sk-your-key-here"


Then restart VS Code or your terminal.

# 5️⃣ Run the Agent
python main.py

🖥 Usage

When you run the program, you’ll see options like:

=== 🤖 AI Gmail Agent ===
1: Reply to incoming emails
2: Compose a new email
3: Send mass email
4: Exit
5: Send daily report manually

Option	Description
1	Fetch unread emails, summarize, and reply automatically
2	Compose a new email manually or use AI
3	Send bulk emails using a CSV list
4	Exit the program
5	NEW: Send AI-analyzed PDF daily report instantly

**✅ The agent will also auto-send your store’s daily report every evening at 8 PM.**

# 🧠 Example: AI-Generated Daily Report Email

Subject:

Daily Report of Store Lavish Sup

Body (AI-generated):

Hello Team,

The attached report summarizes today’s performance for Lavish Sup.

Sales increased by 7% from yesterday.

FMCG category led overall performance.

2 stock alerts detected: Biscuits, Detergent.

You can view full details in the attached report or directly on the RetailEye app.

Best regards,
RetailEye AI Agent

# 📊 Tech Stack

Languages & Frameworks:

🐍 Python 3

🧠 OpenAI GPT (text + report understanding)

📧 Gmail API

📅 Google Calendar API

📦 Pandas, Schedule

🧾 PyPDF2 (PDF text extraction)

🤖 Machine Learning (spam detection)

🌟 Future Enhancements

🖼 Visual Report Understanding – Integrate GPT-4o Vision to analyze charts and graphs from PDF reports.

🔎 Smart Email Priority Ranking – Automatically highlight important emails.

🧩 Insight Summaries – Generate visual insights from multiple store reports.

☁️ SaaS Version – Host RetailEye AI as a multi-user web dashboard.

💬 Multilingual Email Support – Auto-translate and respond in recipient’s preferred language.

# 🤝 Contributing

Contributions are always welcome!

Fork the repo

Open issues or submit pull requests

Share ideas to make RetailEye AI even smarter 🚀

# 📜 License

This project is licensed under the MIT License — free to use, modify, and distribute.

# 👤 Author

Sahil Arora

🌐 GitHub: sahilarora-1



This AI-powered Gmail & Report Agent automatically:

Reads, classifies, and replies to emails,

Analyzes PDF reports using AI,

Generates insightful summary emails, and

Auto-sends them every evening — so you never have to lift a finger again. 💪