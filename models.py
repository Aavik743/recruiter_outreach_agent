from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ContactStatus(Enum):
    VERIFIED_EMAIL = "VERIFIED_EMAIL"
    NAME_ONLY = "NAME_ONLY"
    NO_CONTACT = "NO_CONTACT"


class OutreachAction(Enum):
    READY_TO_SEND = "READY_TO_SEND"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    SKIP = "SKIP"


@dataclass
class Job:
    title: str
    company: str
    description: str
    source_text: str
    location: Optional[str] = None
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
