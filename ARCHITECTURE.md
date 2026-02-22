# Architecture – AI Recruiter Outreach Agent (MVP)

## 1. Modular Architecture Overview

```
[Raw Email Text]
       │
       ▼
  ┌──────────┐
  │  parser   │  parse_jobs() → list[Job]
  └────┬─────┘
       │
       ▼
  ┌──────────┐
  │  scorer   │  score_job(job, master_resume) → int
  └────┬─────┘
       │  skip if score < 75
       ▼
  ┌──────────┐
  │ contact   │  detect_contact(job) → ContactInfo
  └────┬─────┘
       │
       ▼
  ┌──────────┐
  │ resume_gen│  generate_resume_package(job, master_resume) → ResumePackage
  └────┬─────┘
       │
       ▼
  ┌──────────┐
  │ outreach  │  prepare_outreach_decision(job, contact, score, package) → OutreachDecision
  └────┬─────┘
       │
       ▼
  ┌──────────┐
  │ telegram  │  send decision → wait for approval
  └────┬─────┘
       │  user approves
       ▼
  ┌──────────┐
  │  mailer   │  send_email(decision) → bool
  └────┬─────┘
       │
       ▼
  ┌──────────┐
  │ tracker   │  log_to_tracker(entry) → None
  └──────────┘
```

**Control flow lives exclusively in `orchestrator.py`.** Modules never call each other. The orchestrator imports each module and calls functions sequentially.

---

## 2. Folder Structure

```
RecruiterOutreachAgent/
├── AGENTS.md                 # Master control file (immutable)
├── ARCHITECTURE.md           # This file
├── config.py                 # Threshold constants, API credential paths
├── models.py                 # Enums + all dataclasses
├── orchestrator.py           # Main workflow controller
├── modules/
│   ├── __init__.py
│   ├── parser.py             # parse_jobs()
│   ├── scorer.py             # score_job()
│   ├── contact.py            # detect_contact()
│   ├── resume_gen.py         # generate_resume_package()
│   ├── outreach.py           # prepare_outreach_decision()
│   ├── mailer.py             # send_email()
│   └── tracker.py            # log_to_tracker()
├── services/
│   ├── __init__.py
│   ├── gmail_service.py      # Gmail API wrapper
│   ├── sheets_service.py     # Google Sheets API wrapper
│   └── telegram_service.py   # Telegram Bot API wrapper
├── data/
│   └── master_resume.txt     # Plain-text master resume
└── requirements.txt
```

**Rationale:**
- `modules/` — pure business logic, no API calls.
- `services/` — thin wrappers around the three permitted external APIs.
- `models.py` — single source of truth for all data contracts.
- `config.py` — single source of truth for constants.

---

## 3. Enums

```python
# models.py

from enum import Enum


class ContactStatus(Enum):
    VERIFIED_EMAIL = "VERIFIED_EMAIL"
    NAME_ONLY = "NAME_ONLY"
    NO_CONTACT = "NO_CONTACT"


class OutreachAction(Enum):
    READY_TO_SEND = "READY_TO_SEND"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    SKIP = "SKIP"
```

---

## 4. Data Models

```python
# models.py (continued)

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Job:
    title: str
    company: str
    description: str
    source_text: str
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None


@dataclass
class ContactInfo:
    status: ContactStatus
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None


@dataclass
class ResumePackage:
    tailored_resume: str
    cover_letter: str
    job_title: str
    company: str


@dataclass
class OutreachDecision:
    job: Job
    contact: ContactInfo
    match_score: int
    action: OutreachAction
    resume_package: Optional[ResumePackage] = None
    reason: str = ""


@dataclass
class TrackerEntry:
    job_title: str
    company: str
    match_score: int
    contact_status: ContactStatus
    action: OutreachAction
    email_sent: bool
    reason: str = ""
```

---

## 5. Function Signatures

### modules/parser.py

```python
def parse_jobs(raw_email_text: str) -> list[Job]:
    """Parse raw email alert text into structured Job objects.

    Args:
        raw_email_text: The full text body of a job alert email.

    Returns:
        A list of Job instances extracted from the email.
    """
    ...
```

### modules/scorer.py

```python
def score_job(job: Job, master_resume: str) -> int:
    """Score a job against the master resume using deterministic keyword matching.

    Args:
        job: The parsed Job to evaluate.
        master_resume: Plain-text contents of the master resume.

    Returns:
        An integer match score from 0 to 100.
    """
    ...
```

### modules/contact.py

```python
def detect_contact(job: Job) -> ContactInfo:
    """Extract contact information from the parsed job data.

    Determines ContactStatus based on available fields:
    - VERIFIED_EMAIL if recruiter_email is present.
    - NAME_ONLY if only recruiter_name is present.
    - NO_CONTACT if neither is present.

    Args:
        job: The parsed Job to inspect.

    Returns:
        A ContactInfo with the determined status and available details.
    """
    ...
```

### modules/resume_gen.py

```python
def generate_resume_package(job: Job, master_resume: str) -> ResumePackage:
    """Generate a tailored resume and cover letter for a specific job.

    Uses deterministic template substitution — no LLM calls.

    Args:
        job: The target Job.
        master_resume: Plain-text contents of the master resume.

    Returns:
        A ResumePackage containing the tailored resume and cover letter.
    """
    ...
```

### modules/outreach.py

```python
def prepare_outreach_decision(
    job: Job,
    contact: ContactInfo,
    match_score: int,
    resume_package: ResumePackage,
) -> OutreachDecision:
    """Determine the outreach action based on score and contact status.

    Decision matrix:
    - score < threshold         → SKIP
    - NO_CONTACT                → SKIP
    - NAME_ONLY                 → MANUAL_REVIEW
    - VERIFIED_EMAIL            → READY_TO_SEND

    Args:
        job: The target Job.
        contact: The detected ContactInfo.
        match_score: Integer score from score_job().
        resume_package: The generated ResumePackage.

    Returns:
        An OutreachDecision with the appropriate action and reason.
    """
    ...
```

### modules/mailer.py

```python
def send_email(decision: OutreachDecision) -> bool:
    """Send the outreach email via Gmail API.

    Preconditions (caller must enforce):
    - decision.action == READY_TO_SEND
    - decision.contact.status == VERIFIED_EMAIL
    - User has explicitly approved via Telegram

    Args:
        decision: A fully populated OutreachDecision.

    Returns:
        True if the email was sent successfully, False otherwise.
    """
    ...
```

### modules/tracker.py

```python
def log_to_tracker(entry: TrackerEntry) -> None:
    """Append a row to the Google Sheets tracker.

    Args:
        entry: The TrackerEntry to log.
    """
    ...
```

---

## 6. Orchestrator Contract

```python
# orchestrator.py

def run(raw_email_text: str, master_resume: str) -> None:
    """Execute the full pipeline for one email alert.

    Steps:
    1. parse_jobs(raw_email_text) → jobs
    2. For each job:
       a. score_job(job, master_resume) → score
       b. If score < MIN_MATCH_SCORE → log SKIP, continue
       c. detect_contact(job) → contact
       d. If NO_CONTACT → log SKIP, continue
       e. generate_resume_package(job, master_resume) → package
       f. prepare_outreach_decision(job, contact, score, package) → decision
       g. Send decision summary to Telegram
       h. Wait for user approval
       i. If approved and READY_TO_SEND → send_email(decision)
       j. log_to_tracker(entry)
    """
    ...
```

---

## 7. Config Constants

```python
# config.py

MIN_MATCH_SCORE: int = 75
```
