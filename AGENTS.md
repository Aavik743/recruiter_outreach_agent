# AI Recruiter Outreach Agent – Master Control File

## Mission
Build a deterministic, modular AI Recruiter Outreach Agent (MVP).

## Non-Negotiable Constraints

- No LinkedIn scraping
- No browser automation
- No email guessing
- No SMTP probing
- No headless drivers
- No external APIs except:
  - Gmail API
  - Google Sheets API
  - Telegram Bot API
- No LLM API usage
- Deterministic logic preferred over AI inference

## Core Workflow

1. Parse job alerts (raw email text input)
2. Score jobs vs master resume
3. Detect contact status:
   - VERIFIED_EMAIL
   - NAME_ONLY
   - NO_CONTACT
4. Generate tailored resume + cover letter (deterministic)
5. Prepare outreach decision
6. Send structured decision to Telegram
7. Wait for manual approval
8. If approved → send email
9. Log result to Google Sheets

## Contact Rules

Email can ONLY be sent if:
- ContactStatus == VERIFIED_EMAIL
- User explicitly approves

If NAME_ONLY → manual outreach only.
If NO_CONTACT → skip.

## Scoring Rule

Default minimum match score = 75

If match_score < threshold → SKIP.

## Architecture Rules

- Strict modular separation
- No business logic inside Telegram bot
- Orchestrator controls flow
- Modules must not call each other implicitly
- Clean function contracts
- No feature expansion unless explicitly requested
- Do not refactor previous modules unless asked

## Enums

ContactStatus:
- VERIFIED_EMAIL
- NAME_ONLY
- NO_CONTACT

OutreachAction:
- READY_TO_SEND
- MANUAL_REVIEW
- SKIP

## Code Authority Rule

Existing codebase is the single source of truth.
Never redesign architecture unless explicitly requested.
Align with previously defined models and contracts.

## Output Discipline

- Production-ready Python
- No placeholder comments
- No pseudo-code
- No speculative features
- Minimal verbosity