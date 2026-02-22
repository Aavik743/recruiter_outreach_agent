import re

from models import Job, ResumePackage
from modules.scorer import _tokenize, TECHNICAL_SKILLS, STOP_WORDS

_BULLET_RE = re.compile(r'^(\s*[-*•])\s')


def generate_resume_package(
    job: Job,
    master_resume_template: str,
    cover_letter_template: str,
) -> ResumePackage:
    job_keywords = _extract_job_keywords(job)
    tailored_resume = _reorder_bullets(master_resume_template, job_keywords)
    cover_letter = _fill_cover_letter(cover_letter_template, job, job_keywords)
    return ResumePackage(
        tailored_resume=tailored_resume,
        cover_letter=cover_letter,
        job_title=job.title,
        company=job.company,
    )


def _extract_job_keywords(job: Job) -> set[str]:
    desc_tokens = _tokenize(job.description) - STOP_WORDS
    title_tokens = _tokenize(job.title) - STOP_WORDS
    return desc_tokens | title_tokens


def _score_bullet(bullet: str, keywords: set[str]) -> int:
    tokens = _tokenize(bullet)
    matched = tokens & keywords
    skill_hits = len(matched & TECHNICAL_SKILLS)
    general_hits = len(matched - TECHNICAL_SKILLS)
    return skill_hits * 2 + general_hits


def _reorder_bullets(template: str, keywords: set[str]) -> str:
    lines = template.split('\n')
    result: list[str] = []
    bullet_group: list[str] = []

    for line in lines:
        if _BULLET_RE.match(line):
            bullet_group.append(line)
        else:
            if bullet_group:
                bullet_group.sort(
                    key=lambda b: _score_bullet(b, keywords), reverse=True
                )
                result.extend(bullet_group)
                bullet_group = []
            result.append(line)

    if bullet_group:
        bullet_group.sort(
            key=lambda b: _score_bullet(b, keywords), reverse=True
        )
        result.extend(bullet_group)

    return '\n'.join(result)


def _fill_cover_letter(
    template: str, job: Job, keywords: set[str]
) -> str:
    skill_keywords = sorted(keywords & TECHNICAL_SKILLS)
    result = template.replace("{recruiter_name}", job.recruiter_name or "there")
    result = result.replace("{job_title}", job.title)
    result = result.replace("{company}", job.company)
    result = result.replace("{location}", job.location or "")
    result = result.replace("{keywords}", ", ".join(skill_keywords))
    return result
