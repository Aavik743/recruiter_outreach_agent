<!-- DEPLOYMENT_GUIDE_WINDOWS.md -->

# Deployment Guide — Windows Laptop

Step-by-step guide for running the AI Recruiter Outreach Agent on your Windows machine locally.

---

## Prerequisites

- Windows 10 or 11
- Python 3.10 or higher (check with `python --version`)
- A Google account (for Gmail and Sheets APIs)
- A Telegram account
- Git (optional, for cloning the repo)

---

## 1. Environment Setup

### Download the project

Option A: Clone via Git

```cmd
git clone <your-repo-url>
cd RecruiterOutreachAgent
```

Option B: Download ZIP manually

1. Navigate to the GitHub repo.
2. Click **Code** > **Download ZIP**.
3. Extract the ZIP file.
4. Open Command Prompt or PowerShell and navigate to the folder:

```cmd
cd C:\Users\YourName\RecruiterOutreachAgent
```

### Install Python (if needed)

1. Download Python 3.10+ from [python.org](https://www.python.org).
2. Run the installer.
3. **Important**: Check "Add Python to PATH" during installation.
4. Verify installation:

```cmd
python --version
```

### Create a virtual environment

Open **Command Prompt** or **PowerShell** in the project folder and run:

```cmd
python -m venv venv
```

This creates a `venv` folder with an isolated Python environment.

### Activate the virtual environment

**Command Prompt:**

```cmd
venv\Scripts\activate
```

**PowerShell:**

```powershell
venv\Scripts\Activate.ps1
```

If you get an execution policy error in PowerShell, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try the activation command again. You should see `(venv)` in your prompt.

### Install dependencies

```cmd
pip install -r requirements.txt
```

Dependencies installed:

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
4. Wait for the project to initialize.

### Enable the Gmail API

1. Navigate to **APIs & Services** > **Library**.
2. Search for **Gmail API** and click **Enable**.

### Configure OAuth consent screen

1. Go to **APIs & Services** > **OAuth consent screen**.
2. Select **External** user type and click **Create**.
3. Fill in the form:
   - **App name**: `RecruiterAgent`
   - **User support email**: your Gmail address
   - **Developer contact**: your Gmail address
4. Click **Save and Continue**.
5. Skip "Scopes" and "Test users" for now, just click through.
6. On the final screen, add your Gmail address as a test user:
   - Click **Add users** under "Test users".
   - Paste your email and click **Add**.

### Create OAuth credentials

1. Go to **APIs & Services** > **Credentials**.
2. Click **Create Credentials** > **OAuth client ID**.
3. Choose **Application type** > **Desktop app**.
4. Name: `RecruiterAgent Desktop`.
5. Click **Create**.
6. A popup shows your credentials. Click **Download JSON** (or the download icon).
7. Save the JSON file as `credentials.json` in your `RecruiterOutreachAgent` folder (the project root).

### Test Gmail authorization

On first run, a browser opens asking for email access. Grant the permission. A file called `gmail_token.json` is automatically created in the project folder. This token is reused for subsequent runs.

---

## 3. Google Sheets API Setup

### Enable the API

1. In the same Google Cloud project, go to **APIs & Services** > **Library**.
2. Search for **Google Sheets API** and click **Enable**.

### Create the tracker spreadsheet

1. Go to [Google Sheets](https://sheets.google.com).
2. Click **+ Create new spreadsheet**.
3. Name it (e.g., `Recruiter Outreach Tracker`).
4. In **Cell A1**, open the first row and add column headers:

| A          | B       | C           | D              | E      | F          | G      |
|------------|---------|-------------|----------------|--------|------------|--------|
| Job Title  | Company | Match Score | Contact Status | Action | Email Sent | Reason |

5. Keep the sheet name as "Sheet1" (or update configurations if you rename it).

### Get the spreadsheet ID

1. Open the spreadsheet in your browser.
2. Look at the URL:

```
https://docs.google.com/spreadsheets/d/1aBcDeFgHiJkLmNoPqRsTuVwXyZ/edit
```

The long string between `/d/` and `/edit` is your **Spreadsheet ID**:

```
1aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

Save this ID for your `.env` file.

### Test Sheets authorization

On first run, a browser opens asking for Sheets permissions. Grant the access. A file called `sheets_token.json` is automatically created. This thread is reused for subsequent runs.

---

## 4. Telegram Bot Creation

1. Open Telegram and search for **@BotFather**.
2. Send the command `/newbot`.
3. Choose a **display name** (e.g., `My Recruiter Bot`).
4. Choose a **username** ending in `bot` (e.g., `my_recruiter_outreach_bot`).
5. BotFather responds with a **token**:

```
123456789:ABCdefGhIjKlMnOpQrStUvWxYz
```

Copy and save this token for the `.env` file.

### Find your chat ID (optional but useful)

1. Send any message to your bot.
2. In your browser, visit:

```
https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
```

Replace `<YOUR_TOKEN>` with your actual bot token.

3. Look for `"chat":{"id":YOUR_CHAT_ID}` in the JSON response. Save this ID if you need to send messages programmatically.

---

## 5. Environment Variables (.env)

Create a file named `.env` in the project root (`RecruiterOutreachAgent` folder):

**Path**: `C:\Users\YourName\RecruiterOutreachAgent\.env`

**Contents**:

```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIjKlMnOpQrStUvWxYz
SHEETS_SPREADSHEET_ID=1aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

Replace the values with your actual token and spreadsheet ID.

### Loading .env on Windows

The `python-dotenv` package automatically loads the `.env` file when the project runs. No additional setup needed — just ensure the `.env` file is in the project root.

Alternatively, you can set environment variables manually:

**Command Prompt:**

```cmd
set TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIjKlMnOpQrStUvWxYz
set SHEETS_SPREADSHEET_ID=1aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

**PowerShell:**

```powershell
$env:TELEGRAM_BOT_TOKEN="123456789:ABCdefGhIjKlMnOpQrStUvWxYz"
$env:SHEETS_SPREADSHEET_ID="1aBcDeFgHiJkLmNoPqRsTuVwXyZ"
```

---

## 6. Prepare Data Files

### Create the data folder

In the project root, create a folder named `data`:

```cmd
mkdir data
```

Or manually: Right-click in File Explorer → **New** > **Folder** → name it `data`.

### Master resume

1. Open **Notepad** or any text editor.
2. Paste your complete resume in plain text format.
3. Use bullet points (`-` or `*`) for experience items. The agent reorders bullets by relevance to jobs.

Example:

```text
John Doe
john@example.com | (555) 123-4567

EXPERIENCE
Backend Engineer at TechCorp (2020-2023)
- Led Python Django microservices architecture
- Designed PostgreSQL schemas, 50M+ records
- Deployed on AWS ECS and Lambda

SKILLS
Python, Django, PostgreSQL, AWS, Docker, Kubernetes
JavaScript, React, Node.js
Agile, REST APIs, CI/CD
```

4. **Save as**: `data\master_resume.txt` (inside the `data` folder).

### Cover letter template

1. Open **Notepad**.
2. Create a template with placeholders:

```text
Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company}.

Based in {location}, I bring hands-on experience in {keywords}, which align perfectly with your requirements.

I have attached my tailored resume for your review. I am excited to discuss how my background can contribute to your team.

Best regards,
John Doe
(555) 123-4567
john@example.com
```

3. **Save as**: `data\cover_letter_template.txt`.

### Email input

1. Open **Notepad**.
2. Paste the raw text from a job alert email, or compose sample job listings.
3. **Separate each job block with `---`**, `===`, `___`, or `***`.

Example:

```text
Senior Python Developer at Acme Corp
Location: New York, NY
Recruiter: Jane Smith <jane.smith@acme.com>
We are seeking a backend engineer with 5+ years Python experience,
expertise in Django, PostgreSQL, and AWS deployment.
---
Frontend Engineer at Beta Inc
Location: Remote
Hiring Manager: Bob Johnson <bob@betainc.com>
Looking for a React developer with TypeScript and 3+ years experience...
```

4. **Save as**: `data\email_input.txt`.

---

## 7. Running Locally

### Activate the virtual environment

**Command Prompt:**

```cmd
venv\Scripts\activate
```

**PowerShell:**

```powershell
venv\Scripts\Activate.ps1
```

### Run the bot

```cmd
python orchestrator.py
```

You should see output like:

```
INFO:root:Bot starting...
```

The bot is now running and waiting for Telegram commands.

### Use the bot

1. Open Telegram and navigate to your bot.
2. Send `/scan` — the bot parses jobs and presents decisions.
3. Send `/approve <job_id>` to approve and send an email.
4. Send `/skip <job_id>` to skip.
5. Send `/status` to see pending decisions.

### Stop the bot

Press **Ctrl + C** in the Command Prompt or PowerShell window.

---

## 8. Scheduling with Windows Task Scheduler (Optional)

To run the bot automatically at startup or on a schedule:

### Create a batch script

1. Open **Notepad**.
2. Paste:

```batch
@echo off
cd C:\Users\YourName\RecruiterOutreachAgent
call venv\Scripts\activate.bat
python orchestrator.py
pause
```

Replace `YourName` with your Windows username.

3. **Save as**: `run_bot.bat` in the project root.

### Schedule the task

1. Press **Windows Key + R**, type `taskschd.msc`, and press **Enter**.
2. Click **Create Task** (right panel).
3. **General** tab:
   - **Name**: `Recruiter Bot`
   - Check **Run whether user is logged in or not** (if you have admin privileges).
   - Check **Run with highest privileges**.
4. **Triggers** tab:
   - Click **New**.
   - Choose **At startup** (or **On a schedule** for periodic runs).
   - Click **OK**.
5. **Actions** tab:
   - Click **New**.
   - **Program/script**: `C:\Users\YourName\RecruiterOutreachAgent\run_bot.bat`
   - Click **OK**.
6. **Settings** tab:
   - Check **Allow task to be run on demand**.
   - Check **Run task as soon as possible after a scheduled start is missed**.
7. Click **OK** to save the task.

### Run or stop the task

- **Run now**: Right-click the task in Task Scheduler → **Run**.
- **Stop**: Right-click the task → **End**.
- **View logs**: Double-click the task → **History** tab.

---

## 9. Important Notes for Windows

### File paths

Windows uses backslashes (`\`). The config file already handles this, but if you specify custom paths in `.env`, use either:

- Forward slashes: `data/master_resume.txt`
- Escaped backslashes: `data\\master_resume.txt`

### Firewall

The bot connects to Telegram's API over the internet. Windows Firewall may prompt on first run. Click **Allow** to permit the connection.

### Temporary files

The orchestrator creates temporary resume and cover letter files during email sending. These are cleaned up automatically. If the process crashes, temporary files may remain in the system temp folder (`C:\Users\YourName\AppData\Local\Temp\`). This is safe to ignore.

### Logs

To save logs to a file for troubleshooting:

```cmd
python orchestrator.py >> bot.log 2>&1
```

This appends all output to `bot.log` in the project folder. You can open `bot.log` with Notepad to review past errors.

---

## 10. Troubleshooting

| Issue                                  | Solution                                                        |
|----------------------------------------|-----------------------------------------------------------------|
| `python: command not found`            | Python not in PATH. Re-run installer with "Add Python to PATH" checked, or manually add `C:\Program Files\Python311\` to PATH. |
| `No module named 'telegram'`           | Virtual environment not activated. Run `venv\Scripts\activate`. |
| `FileNotFoundError: credentials.json`  | OAuth credentials file is missing. Download from Google Cloud Console and save as `credentials.json` in project root. |
| Bot does not respond on Telegram       | Verify `TELEGRAM_BOT_TOKEN` in `.env`. Ensure bot is running in Command Prompt/PowerShell. Try `/ping` or `/status`. |
| "OAuth consent screen not configured"  | Go to Google Cloud Console OAuth consent screen and add your Gmail as a test user. |
| Email not sent on `/approve`           | Verify contact status is `VERIFIED_EMAIL` in the Telegram message. Check Gmail token: delete `gmail_token.json` and re-run to re-authorize. |
| "No jobs found" on `/scan`             | Check `data\email_input.txt` exists and contains job blocks separated by `---`. |
| `.env` variables not loading           | Ensure `.env` file is in the project root (same folder as `orchestrator.py`). Restart the bot after creating `.env`. |

---

## 11. Next Steps

- Regularly update `data\master_resume.txt` to improve scoring accuracy.
- Use the Google Sheet tracker to monitor your outreach history.
- For production deployments on cloud servers, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

---

## Further Help

- **Bot usage**: See [USER_GUIDE.md](USER_GUIDE.md).
- **Architecture details**: See [ARCHITECTURE.md](ARCHITECTURE.md).
- **Core constraints**: See [AGENTS.md](AGENTS.md).
