from models import ContactInfo, ContactStatus, Job


def detect_contact(job: Job) -> ContactInfo:
    if job.recruiter_email:
        return ContactInfo(
            status=ContactStatus.VERIFIED_EMAIL,
            recruiter_name=job.recruiter_name,
            recruiter_email=job.recruiter_email,
        )

    if job.recruiter_name:
        return ContactInfo(
            status=ContactStatus.NAME_ONLY,
            recruiter_name=job.recruiter_name,
        )

    return ContactInfo(status=ContactStatus.NO_CONTACT)
