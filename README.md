<!-- README.md -->

# AI Recruiter Outreach Agent

A deterministic, modular agent that parses job alerts, scores them against your resume, and sends personalized outreach emails — with manual approval via Telegram.

---

## How It Works

1. **Parse** job alert emails into structured data.
2. **Score** each job against your master resume using keyword matching.
3. **Detect** recruiter contact information.
4. **Generate** a tailored resume and cover letter.
5. **Present** each decision to you via Telegram.
6. **Wait** for your explicit `/approve` or `/skip`.
7. **Send** email with attachments (only with verified email + your approval).
8. **Log** every result to a Google Sheet.

No AI/LLM APIs. Fully deterministic. You control every outreach.

---

## Documentation

| Document                                           | Contents                                    |
|----------------------------------------------------|---------------------------------------------|
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)         | Setup and deployment for Linux/cloud        |
| [DEPLOYMENT_GUIDE_WINDOWS.md](DEPLOYMENT_GUIDE_WINDOWS.md) | Setup for Windows laptop              |
| [USER_GUIDE.md](USER_GUIDE.md)                     | Bot usage, commands, and workflow             |
| [ARCHITECTURE.md](ARCHITECTURE.md)                 | Module design and function contracts          |
| [AGENTS.md](AGENTS.md)                             | Master control file and constraints           |

---

## Quick Start

### 1. Clone and install

```bash
git clone <your-repo-url>
cd RecruiterOutreachAgent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set up credentials

- Place your Google OAuth `credentials.json` in the project root (see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for full instructions).
- Create a Telegram bot via @BotFather and get the token.
- Create a Google Sheet with the tracker schema.

### 3. Configure environment

Create a `.env` file:

```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
SHEETS_SPREADSHEET_ID=your_google_sheets_id
```

### 4. Prepare data files

```bash
mkdir -p data
```

- `data/master_resume.txt` — Your full resume in plain text.
- `data/cover_letter_template.txt` — Cover letter with `{job_title}`, `{company}`, `{location}`, `{keywords}` placeholders.
- `data/email_input.txt` — Raw job alert email text (job blocks separated by `---`).

### 5. Start the bot

```bash
set -a && source .env && set +a
python orchestrator.py
```

### 6. Use via Telegram

| Command              | Action                            |
|----------------------|-----------------------------------|
| `/scan`              | Scan and score job alerts         |
| `/approve <job_id>`  | Approve and send email            |
| `/skip <job_id>`     | Skip and log                      |
| `/status`            | View pending decisions            |

---

## Project Structure

```
RecruiterOutreachAgent/
├── orchestrator.py           # Main workflow controller
├── config.py                 # Configuration constants
├── models.py                 # Enums and dataclasses
├── modules/
│   ├── parser.py             # Job alert parser
│   ├── scorer.py             # Resume-job scorer
│   ├── contact.py            # Contact detection
│   ├── resume.py             # Resume/cover letter generation
│   └── decision.py           # Outreach decision logic
├── services/
│   ├── telegram_service.py   # Telegram Bot wrapper
│   ├── gmail_service.py      # Gmail API wrapper
│   └── sheets_service.py     # Google Sheets wrapper
├── data/
│   ├── master_resume.txt     # Your resume
│   ├── cover_letter_template.txt
│   └── email_input.txt       # Job alert input
├── requirements.txt
├── AGENTS.md                 # Constraints and rules
├── ARCHITECTURE.md           # Design and contracts
├── DEPLOYMENT_GUIDE.md       # Setup instructions
└── USER_GUIDE.md             # Usage guide
```

---

## Constraints

- No LinkedIn scraping, browser automation, or email guessing.
- No LLM API calls — all logic is deterministic.
- External APIs limited to: Gmail API, Google Sheets API, Telegram Bot API.
- Email is only sent with verified recruiter email and explicit user approval.

See [AGENTS.md](AGENTS.md) for the full constraint set.
