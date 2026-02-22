import re
from typing import Optional

from models import Job


_BLOCK_SEPARATOR = re.compile(r'^\s*[-=_*]{3,}\s*$', re.MULTILINE)

_EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

_TITLE_LABEL_RE = re.compile(
    r'(?:job\s*title|role|position)\s*:\s*(.+)', re.IGNORECASE,
)
_COMPANY_LABEL_RE = re.compile(
    r'(?:company|employer|organization)\s*:\s*(.+)', re.IGNORECASE,
)
_LOCATION_LABEL_RE = re.compile(
    r'(?:location|city|place)\s*:\s*(.+)', re.IGNORECASE,
)

_TITLE_AT_COMPANY_RE = re.compile(r'^(.+?)\s+at\s+(.+?)$', re.MULTILINE)

_COMPANY_LOCATION_SEP_RE = re.compile(r'^(.+?)\s+[-|·–—]\s+(.+?)$')

_RECRUITER_LABEL_RE = re.compile(
    r'(?i:(?:recruiter|posted\s+by|contact|hiring\s+manager))\s*:\s*'
    r'([A-Z][a-zA-Z]+(?:[ \t]+[A-Z][a-zA-Z]+)+)',
)

_CITY_STATE_RE = re.compile(
    r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*,\s*[A-Z]{2})\b',
)

_REMOTE_RE = re.compile(r'\bremote\b', re.IGNORECASE)

_IGNORED_EMAIL_PREFIXES = frozenset({
    'noreply', 'no-reply', 'unsubscribe', 'mailer-daemon', 'postmaster',
    'notifications', 'alert', 'alerts', 'donotreply', 'do-not-reply',
})

_MAX_FIELD_WORDS = 10


def parse_jobs(raw_email_text: str) -> list[Job]:
    blocks = _split_blocks(raw_email_text)
    jobs: list[Job] = []
    for block in blocks:
        job = _parse_block(block)
        if job is not None:
            jobs.append(job)
    return jobs


def _split_blocks(text: str) -> list[str]:
    parts = _BLOCK_SEPARATOR.split(text)
    return [p.strip() for p in parts if p.strip()]


def _parse_block(block: str) -> Optional[Job]:
    title = _extract_labeled_field(_TITLE_LABEL_RE, block)
    company = _extract_labeled_field(_COMPANY_LABEL_RE, block)
    location = _extract_labeled_field(_LOCATION_LABEL_RE, block)

    if not title and not company:
        first_lines = '\n'.join(block.splitlines()[:3])
        match = _TITLE_AT_COMPANY_RE.search(first_lines)
        if match:
            title = match.group(1).strip()
            company = _clean_company(match.group(2).strip())

    if not title or not company:
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if lines and not title and len(lines[0].split()) <= _MAX_FIELD_WORDS:
            title = lines[0]
        if len(lines) >= 2 and not company:
            candidate = lines[1]
            if len(candidate.split()) <= _MAX_FIELD_WORDS:
                company, pos_location = _parse_company_line(candidate)
                if not location and pos_location:
                    location = pos_location

    if not title or not company:
        return None

    company = _clean_company(company)

    if not location:
        location = _extract_location_fallback(block)

    email = _extract_email(block)
    recruiter_name = _extract_recruiter_name(block, email)

    return Job(
        title=title,
        company=company,
        location=location,
        description=block,
        source_text=block,
        recruiter_name=recruiter_name,
        recruiter_email=email,
    )


def _extract_labeled_field(
    pattern: re.Pattern[str], text: str,
) -> Optional[str]:
    match = pattern.search(text)
    if match:
        return match.group(1).strip()
    return None


def _parse_company_line(line: str) -> tuple[str, Optional[str]]:
    match = _COMPANY_LOCATION_SEP_RE.match(line)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return line, None


def _clean_company(raw: str) -> str:
    for sep in (' - ', ' | ', ' · ', ' – ', ' — '):
        if sep in raw:
            return raw.split(sep)[0].strip()
    return raw.strip()


def _extract_location_fallback(text: str) -> Optional[str]:
    match = _CITY_STATE_RE.search(text)
    if match:
        return match.group(1)
    if _REMOTE_RE.search(text):
        return 'Remote'
    return None


def _extract_email(text: str) -> Optional[str]:
    for match in _EMAIL_RE.finditer(text):
        email = match.group(0)
        local_part = email.split('@')[0].lower()
        if local_part not in _IGNORED_EMAIL_PREFIXES:
            return email
    return None


def _extract_recruiter_name(
    text: str, email: Optional[str],
) -> Optional[str]:
    match = _RECRUITER_LABEL_RE.search(text)
    if match:
        return match.group(1).strip()
    if email:
        escaped = re.escape(email)
        pattern = rf'([A-Z][a-zA-Z]+(?:[ \t]+[A-Z][a-zA-Z]+)+)[ \t]*<?{escaped}'
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return None
