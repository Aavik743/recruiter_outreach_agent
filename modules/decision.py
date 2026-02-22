from config import MIN_MATCH_SCORE
from models import (
    ContactInfo,
    ContactStatus,
    Job,
    OutreachAction,
    OutreachDecision,
)


def prepare_outreach_decision(
    job: Job,
    contact_status: ContactStatus,
    match_score: int,
) -> OutreachDecision:
    contact = ContactInfo(
        status=contact_status,
        recruiter_name=job.recruiter_name,
        recruiter_email=job.recruiter_email,
    )

    if match_score < MIN_MATCH_SCORE:
        return OutreachDecision(
            job=job,
            contact=contact,
            match_score=match_score,
            action=OutreachAction.SKIP,
            reason=f"Match score {match_score} below minimum {MIN_MATCH_SCORE}",
        )

    if contact_status == ContactStatus.VERIFIED_EMAIL:
        return OutreachDecision(
            job=job,
            contact=contact,
            match_score=match_score,
            action=OutreachAction.READY_TO_SEND,
            reason="Verified email available",
        )

    if contact_status == ContactStatus.NAME_ONLY:
        return OutreachDecision(
            job=job,
            contact=contact,
            match_score=match_score,
            action=OutreachAction.MANUAL_REVIEW,
            reason="Recruiter name found but no verified email",
        )

    return OutreachDecision(
        job=job,
        contact=contact,
        match_score=match_score,
        action=OutreachAction.SKIP,
        reason="No contact information available",
    )
