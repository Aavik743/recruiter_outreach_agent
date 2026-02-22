import logging
import threading
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

import config
from models import (
    ContactStatus,
    OutreachAction,
    OutreachDecision,
    TrackerEntry,
)
from modules.parser import parse_jobs
from modules.scorer import score_job
from modules.contact import detect_contact
from modules.resume import generate_resume_package
from modules.decision import prepare_outreach_decision
from services.gmail_service import send_email
from services.sheets_service import append_row
from services.telegram_service import TelegramBot, format_decision

logger = logging.getLogger(__name__)

_counter_lock = threading.Lock()
_counter = 0


def _next_job_id() -> str:
    global _counter
    with _counter_lock:
        _counter += 1
        return str(_counter)


def _load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _build_tracker_entry(
    decision: OutreachDecision, email_sent: bool
) -> TrackerEntry:
    return TrackerEntry(
        job_title=decision.job.title,
        company=decision.job.company,
        match_score=decision.match_score,
        contact_status=decision.contact.status,
        action=decision.action,
        email_sent=email_sent,
        reason=decision.reason,
    )


def run(
    raw_email_text: str,
    master_resume: str,
    cover_letter_template: str,
) -> tuple[list[str], list[tuple[str, OutreachDecision]]]:
    """Execute the pipeline for one email alert.

    Steps:
        1. parse_jobs → list of jobs
        2. For each job: score, detect contact, generate package, decide
        3. Log early SKIPs to tracker immediately
        4. Return actionable decisions for Telegram approval

    Returns:
        Tuple of (summary_lines, pending_decisions).
        summary_lines: Formatted strings for Telegram display.
        pending_decisions: (job_id, OutreachDecision) pairs needing user action.
    """
    jobs = parse_jobs(raw_email_text)
    if not jobs:
        return ["No jobs found in the provided email text."], []

    summary: list[str] = []
    pending: list[tuple[str, OutreachDecision]] = []

    for job in jobs:
        score = score_job(job, master_resume)

        if score < config.MIN_MATCH_SCORE:
            contact = detect_contact(job)
            entry = TrackerEntry(
                job_title=job.title,
                company=job.company,
                match_score=score,
                contact_status=contact.status,
                action=OutreachAction.SKIP,
                email_sent=False,
                reason=(
                    f"Match score {score} below "
                    f"minimum {config.MIN_MATCH_SCORE}"
                ),
            )
            append_row(entry)
            summary.append(
                f"SKIP: {job.title} @ {job.company} (score: {score})"
            )
            continue

        contact = detect_contact(job)

        if contact.status == ContactStatus.NO_CONTACT:
            entry = TrackerEntry(
                job_title=job.title,
                company=job.company,
                match_score=score,
                contact_status=contact.status,
                action=OutreachAction.SKIP,
                email_sent=False,
                reason="No contact information available",
            )
            append_row(entry)
            summary.append(
                f"SKIP: {job.title} @ {job.company} (no contact)"
            )
            continue

        package = generate_resume_package(
            job, master_resume, cover_letter_template
        )

        decision = prepare_outreach_decision(job, contact.status, score)
        decision.resume_package = package

        job_id = _next_job_id()
        pending.append((job_id, decision))
        summary.append(format_decision(job_id, decision))

    return summary, pending


def handle_approve(job_id: str, decision: OutreachDecision) -> str:
    """Handle user approval of an outreach decision.

    Sends email only when all conditions are met:
        - action is READY_TO_SEND
        - contact status is VERIFIED_EMAIL
        - resume_package is present

    Logs result to Google Sheets tracker.
    """
    email_sent = False

    if (
        decision.action == OutreachAction.READY_TO_SEND
        and decision.contact.status == ContactStatus.VERIFIED_EMAIL
        and decision.resume_package
    ):
        email_sent = send_email(
            decision.job,
            config.RESUME_PDF_PATH,
            decision.resume_package.cover_letter,
        )

    entry = _build_tracker_entry(decision, email_sent)
    append_row(entry)

    if email_sent:
        return (
            f"Approved [{job_id}]: Email sent to "
            f"{decision.contact.recruiter_email}"
        )
    return f"Approved [{job_id}]: Logged (email not sent)"


def handle_skip(job_id: str, decision: OutreachDecision) -> str:
    """Handle user skip of an outreach decision. Log to tracker."""
    entry = _build_tracker_entry(decision, email_sent=False)
    entry.action = OutreachAction.SKIP
    entry.reason = "Skipped by user"
    append_row(entry)
    return f"Skipped [{job_id}]: {decision.job.title} @ {decision.job.company}"


def handle_status(pending: dict[str, OutreachDecision]) -> str:
    """Format all pending decisions for /status display."""
    if not pending:
        return "No pending decisions."
    lines = []
    for job_id, d in pending.items():
        lines.append(
            f"[{job_id}] {d.job.title} @ {d.job.company} "
            f"(score: {d.match_score}, action: {d.action.value})"
        )
    return "Pending decisions:\n" + "\n".join(lines)


def main() -> None:
    """Entry point: configure bot callbacks and start polling."""
    bot = TelegramBot(config.TELEGRAM_BOT_TOKEN)

    master_resume = _load_text(config.MASTER_RESUME_PATH)
    cover_template = _load_text(config.COVER_LETTER_TEMPLATE_PATH)

    def on_scan() -> str:
        raw_text = _load_text(config.EMAIL_INPUT_PATH)
        summaries, decisions = run(raw_text, master_resume, cover_template)
        for job_id, decision in decisions:
            bot.add_pending(job_id, decision)
        return "\n\n".join(summaries) if summaries else "No jobs found."

    bot.set_handlers(
        on_scan=on_scan,
        on_approve=handle_approve,
        on_skip=handle_skip,
        on_status=handle_status,
    )

    logger.info("Bot starting...")
    bot.run()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    main()
