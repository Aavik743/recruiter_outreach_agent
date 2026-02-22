<!-- USER_GUIDE.md -->

# User Guide — AI Recruiter Outreach Agent

How to use the Telegram bot after deployment.

---

## Starting the Bot

Ensure all setup steps in [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) are complete, then run:

```bash
source venv/bin/activate
set -a && source .env && set +a
python orchestrator.py
```

The bot starts polling. Open Telegram and navigate to your bot.

---

## Telegram Commands

| Command              | Description                                              |
|----------------------|----------------------------------------------------------|
| `/scan`              | Parse job alerts, score jobs, and present decisions       |
| `/approve <job_id>`  | Approve a pending decision — sends email if eligible     |
| `/skip <job_id>`     | Skip a pending decision — logs as skipped to tracker     |
| `/status`            | List all pending decisions awaiting your action           |

---

## Typical Workflow

### 1. Prepare input

Place raw job alert email text in `data/email_input.txt`. The parser splits on separators (`---`, `===`, `___`, `***`), so each job block should be separated by one of these.

Example content:

```text
Senior Python Developer at Acme Corp
Location: New York, NY
Recruiter: Jane Smith <jane.smith@acme.com>
We are looking for an experienced Python developer with
expertise in Django, PostgreSQL, and AWS...
---
Frontend Engineer at Beta Inc
Location: Remote
We need a React/TypeScript developer...
```

### 2. Scan jobs

Send `/scan` in Telegram. The bot:

1. Parses all job blocks from the input file.
2. Scores each job against your master resume.
3. Detects recruiter contact information.
4. Generates a tailored resume and cover letter.
5. Prepares an outreach decision for each job.

You receive a summary message for each job:

```
--- Job [1] ---
Title:   Senior Python Developer
Company: Acme Corp
Score:   87
Contact: VERIFIED_EMAIL
Action:  READY_TO_SEND
Reason:  Verified email available
Email:   jane.smith@acme.com

/approve 1  or  /skip 1
```

Jobs that are automatically skipped (low score or no contact) are logged to the tracker immediately and shown as `SKIP` in the summary.

### 3. Review and decide

For each pending decision, choose:

- `/approve 1` — Approves the decision. If the action is `READY_TO_SEND` and a verified email exists, the agent sends an email with your tailored resume and cover letter attached.
- `/skip 1` — Skips the decision. Logged to the tracker as skipped by user.

### 4. Check pending

Send `/status` at any time to see all decisions still awaiting your action:

```
Pending decisions:
[1] Senior Python Developer @ Acme Corp (score: 87, action: READY_TO_SEND)
[3] Data Engineer @ Gamma LLC (score: 82, action: MANUAL_REVIEW)
```

### 5. Track results

All decisions (approved, skipped, auto-skipped) are logged to your Google Sheet with full details.

---

## Decision Actions Explained

| Action          | Meaning                                          | What happens on /approve                  |
|-----------------|--------------------------------------------------|-------------------------------------------|
| READY_TO_SEND   | Verified email found, score above threshold      | Email sent with resume and cover letter    |
| MANUAL_REVIEW   | Recruiter name found but no verified email       | Logged to tracker, no email sent           |
| SKIP            | Low score or no contact info                     | Auto-logged during scan, not shown as pending |

---

## Email Sending

### When emails are sent

Emails are sent **only** when all conditions are met:

1. Contact status is `VERIFIED_EMAIL`.
2. Decision action is `READY_TO_SEND`.
3. You explicitly approve via `/approve <job_id>`.

No email is ever sent automatically.

### What the email contains

- **To**: The recruiter's verified email address.
- **Subject**: `Application: <Job Title> at <Company>`.
- **Body**: Brief introduction addressing the recruiter by name (or "Hiring Manager").
- **Attachments**: Tailored resume and cover letter as text files.

### Personalization

The resume and cover letter are tailored per job:

- Resume bullets are reordered by relevance to the job description.
- Technical skill matches are weighted more heavily.
- Cover letter template placeholders (`{job_title}`, `{company}`, `{location}`, `{keywords}`) are filled with job-specific values.

---

## Best Practices

- **Update your master resume** (`data/master_resume.txt`) regularly to improve scoring accuracy.
- **Use bullet points** (`-` or `*`) in the master resume — the agent reorders bullets by relevance.
- **Review decisions before approving** — check the score, contact info, and action before sending emails.
- **Keep the cover letter template professional** — it is filled deterministically, so the template quality directly affects outreach quality.
- **Process one email alert at a time** — replace `data/email_input.txt` contents before each `/scan`.
- **Monitor the Google Sheet** — it serves as your outreach CRM with full history.

---

## Troubleshooting

| Issue                              | Solution                                                        |
|------------------------------------|-----------------------------------------------------------------|
| `/scan` returns "No jobs found"    | Check `data/email_input.txt` format. Ensure job blocks are separated by `---` or similar. |
| Bot does not respond               | Verify the bot is running. Check `TELEGRAM_BOT_TOKEN`. Ensure only one instance is running. |
| "Scan handler not configured"      | The orchestrator did not wire callbacks. Restart the bot.       |
| "No pending decision for job_id"   | The decision was already approved/skipped, or the bot restarted (pending state is in-memory). |
| Email not sent on approve          | Verify contact status is `VERIFIED_EMAIL` and action is `READY_TO_SEND`. Check Gmail token validity. |
| Sheets logging fails               | Verify `SHEETS_SPREADSHEET_ID`. Check Google Sheets API is enabled. Re-authorize if token expired. |
| Low scores for relevant jobs       | Update `data/master_resume.txt` with more keywords matching the job descriptions. |
| OAuth browser window not opening   | Ensure you are running on a machine with a browser. For headless servers, authorize locally first and transfer token files. |
