<!-- DEPLOYMENT_GUIDE.md -->

# Deployment Guide — AI Recruiter Outreach Agent

Complete step-by-step guide for deploying the agent on free Linux-based infrastructure.

---

## Prerequisites

- Python 3.10 or higher
- A Google account (for Gmail and Sheets APIs)
- A Telegram account

---

## 1. Environment Setup

### Clone and enter the project

```bash
git clone <your-repo-url>
cd RecruiterOutreachAgent
```

### Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

The `requirements.txt` includes:

| Package                    | Purpose                  |
|----------------------------|--------------------------|
| python-telegram-bot        | Telegram Bot API         |
| google-api-python-client   | Gmail and Sheets APIs    |
| google-auth-oauthlib       | OAuth2 authentication    |
| google-auth                | Google credential mgmt   |
| python-dotenv              | Load .env variables      |

---

## 2. Gmail API OAuth Setup

### Create a Google Cloud project

1. Go to [Google Cloud Console](https://console.cloud.google.com).
2. Click **Select a project** > **New Project**.
3. Name it (e.g., `RecruiterAgent`) and click **Create**.

### Enable the Gmail API

1. Navigate to **APIs & Services** > **Library**.
2. Search for **Gmail API** and click **Enable**.

### Configure OAuth consent screen

1. Go to **APIs & Services** > **OAuth consent screen**.
2. Select **External** user type and click **Create**.
3. Fill in:
   - App name: `RecruiterAgent`
   - User support email: your email
   - Developer contact: your email
4. Click **Save and Continue** through the remaining steps.
5. Under **Test users**, click **Add users** and add your Gmail address.

### Create OAuth credentials

1. Go to **APIs & Services** > **Credentials**.
2. Click **Create Credentials** > **OAuth client ID**.
3. Application type: **Desktop app**.
4. Name it (e.g., `RecruiterAgent Desktop`).
5. Click **Create**, then **Download JSON**.
6. Save the file as `credentials.json` in the project root.

### First-run authorization

On first run, a browser window opens asking you to grant **Send email** permission. After granting, a `gmail_token.json` file is saved locally for subsequent runs.

---

## 3. Google Sheets API Setup

### Enable the API

1. In the same Google Cloud project, go to **APIs & Services** > **Library**.
2. Search for **Google Sheets API** and click **Enable**.

### Create the tracker spreadsheet

1. Go to [Google Sheets](https://sheets.google.com) and create a new spreadsheet.
2. Name it (e.g., `Recruiter Outreach Tracker`).
3. Add headers in **Row 1**:

| A          | B       | C           | D              | E      | F          | G      |
|------------|---------|-------------|----------------|--------|------------|--------|
| Job Title  | Company | Match Score | Contact Status | Action | Email Sent | Reason |

4. Copy the **spreadsheet ID** from the URL:

```
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit
```

The long string between `/d/` and `/edit` is your spreadsheet ID.

### Permissions

The Google account that authorizes the Sheets API must have **Editor** access to the spreadsheet. If you created the spreadsheet with the same account, this is already the case.

### First-run authorization

On first run, a browser window asks for Sheets read/write permission. After granting, `sheets_token.json` is saved locally.

---

## 4. Telegram Bot Creation

1. Open Telegram and search for **@BotFather**.
2. Send `/newbot`.
3. Choose a display name (e.g., `Recruiter Outreach Bot`).
4. Choose a username ending in `bot` (e.g., `my_recruiter_outreach_bot`).
5. BotFather responds with a **token** like:

```
123456789:ABCdefGhIjKlMnOpQrStUvWxYz
```

6. Save this token for the `.env` file.

### Find your chat ID

1. Send any message to your new bot.
2. Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser.
3. Look for `"chat":{"id":YOUR_CHAT_ID}` in the response.

---

## 5. Environment Variables (.env)

Create a `.env` file in the project root:

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIjKlMnOpQrStUvWxYz
SHEETS_SPREADSHEET_ID=1aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

Load the variables before running:

```bash
set -a
source .env
set +a
```

Or export inline:

```bash
export $(grep -v '^#' .env | xargs)
```

---

## 6. Prepare Data Files

```bash
mkdir -p data
```

### Master resume

Create `data/master_resume.txt` with your full resume in plain text. Use bullet points (`-` or `*`) for experience items — the agent reorders bullets by job relevance.

### Cover letter template

Create `data/cover_letter_template.txt` using these placeholders:

```text
Dear Hiring Manager,

I am writing to express my interest in the {job_title} position at {company}.
Based in {location}, I bring experience in {keywords}.

I have attached my tailored resume for your review.

Best regards,
Your Name
```

### Email input

Place the raw text of a job alert email into `data/email_input.txt`. The parser expects job blocks separated by `---`, `===`, `___`, or `***`.

---

## 7. Running Locally

```bash
source venv/bin/activate
set -a && source .env && set +a
python orchestrator.py
```

The bot starts polling Telegram. Open your bot chat and send `/scan`.

---

## 8. Scheduling with Cron

The bot runs continuously via long-polling. Use **systemd** for persistent operation or **cron** for periodic restarts.

### Systemd service (recommended)

Create `/etc/systemd/system/recruiter-bot.service`:

```ini
[Unit]
Description=Recruiter Outreach Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/RecruiterOutreachAgent
EnvironmentFile=/home/ubuntu/RecruiterOutreachAgent/.env
ExecStart=/home/ubuntu/RecruiterOutreachAgent/venv/bin/python orchestrator.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable recruiter-bot
sudo systemctl start recruiter-bot
```

Check status:

```bash
sudo systemctl status recruiter-bot
sudo journalctl -u recruiter-bot -f
```

### Cron alternative

If you prefer cron for periodic scanning (not continuous polling), create a runner script:

```bash
#!/usr/bin/env bash
cd /home/ubuntu/RecruiterOutreachAgent
source venv/bin/activate
set -a && source .env && set +a
python orchestrator.py
```

Save as `run.sh`, then:

```bash
chmod +x run.sh
crontab -e
```

Add (runs daily at 9 AM):

```
0 9 * * * /home/ubuntu/RecruiterOutreachAgent/run.sh >> /home/ubuntu/RecruiterOutreachAgent/bot.log 2>&1
```

---

## 9. Free Cloud Hosting (Optional)

### Railway

1. Push your repo to GitHub.
2. Sign up at [railway.app](https://railway.app) (free tier available).
3. **New Project** > **Deploy from GitHub repo**.
4. Add environment variables in the Railway dashboard:
   - `TELEGRAM_BOT_TOKEN`
   - `SHEETS_SPREADSHEET_ID`
5. Set start command: `python orchestrator.py`.
6. Upload `credentials.json`, `gmail_token.json`, and `sheets_token.json` to the Railway filesystem or use Railway volumes.

### Fly.io

1. Install `flyctl`:

```bash
curl -L https://fly.io/install.sh | sh
```

2. Initialize and deploy:

```bash
fly launch --name recruiter-bot
fly secrets set TELEGRAM_BOT_TOKEN=your_token SHEETS_SPREADSHEET_ID=your_id
fly deploy
```

3. For OAuth token files, use Fly volumes:

```bash
fly volumes create data --size 1
```

Mount in `fly.toml` and copy token files to the volume.

### Important cloud hosting notes

- **OAuth tokens**: Run the bot locally first to complete OAuth authorization and generate `gmail_token.json` and `sheets_token.json`. Then deploy these files to your cloud environment.
- **Headless servers**: The initial OAuth flow opens a browser. Complete this step on a machine with a browser, then transfer the token files.
- **Free tier limits**: Both Railway and Fly.io have monthly hour limits on free tiers. Monitor usage.

---

## 10. Important Notes and Troubleshooting

### Token expiry

Google OAuth tokens expire periodically. If the bot fails with auth errors:

```bash
rm gmail_token.json sheets_token.json
python orchestrator.py  # re-authorize
```

### Bot not responding

- Verify `TELEGRAM_BOT_TOKEN` is correct.
- Ensure no other instance of the bot is running (only one poller per token).
- Check network connectivity to `api.telegram.org`.

### Sheets permission denied

- Confirm the Google account that authorized the API has Editor access to the spreadsheet.
- Verify `SHEETS_SPREADSHEET_ID` matches the target spreadsheet.

### OAuth consent screen errors

- If you see "Access blocked: This app's request is invalid," ensure your email is added as a test user in the Cloud Console OAuth consent screen.
- Apps in "Testing" mode allow up to 100 test users.

### File not found errors

- Ensure `data/master_resume.txt`, `data/cover_letter_template.txt`, and `data/email_input.txt` exist.
- Ensure `credentials.json` is in the project root.

### Logs

The orchestrator logs to stdout. Redirect to a file for persistent logging:

```bash
python orchestrator.py >> bot.log 2>&1
```

Or use systemd journal:

```bash
sudo journalctl -u recruiter-bot --since "1 hour ago"
```
