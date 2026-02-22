"""Gmail API service wrapper.

OAuth Setup:
    1. Go to Google Cloud Console (console.cloud.google.com).
    2. Create a project or select an existing one.
    3. Enable the Gmail API under "APIs & Services" > "Library."
    4. Go to "APIs & Services" > "Credentials."
    5. Click "Create Credentials" > "OAuth client ID."
    6. Select "Desktop app" as the application type.
    7. Download the JSON file and save it as credentials.json
       in the project root (or the path set in config.GMAIL_CREDENTIALS_PATH).
    8. On first run, a browser window opens for authorization.
       Grant "Send email" permission. A token is saved to gmail_token.json
       for subsequent runs.
"""

import base64
import logging
import mimetypes
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import config
from models import Job

logger = logging.getLogger(__name__)

_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def _authenticate():
    """Build and return an authenticated Gmail API service."""
    creds = None
    token_path = Path(config.GMAIL_TOKEN_PATH)
    creds_path = Path(config.GMAIL_CREDENTIALS_PATH)

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), _SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_path.exists():
                raise FileNotFoundError(
                    f"OAuth credentials file not found: {creds_path}. "
                    "See module docstring for setup instructions."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(creds_path), _SCOPES
            )
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def send_email(job: Job, resume_path: str, cover_letter: str) -> bool:
    """Send outreach email with resume attached and cover letter as body.

    Preconditions (caller must enforce):
        - job.recruiter_email is not None.
        - User has explicitly approved via Telegram.

    Args:
        job: Job with verified recruiter_email.
        resume_path: Path to the resume PDF file.
        cover_letter: Cover letter text used as the email body.

    Returns:
        True if sent successfully, False otherwise.
    """
    if not job.recruiter_email:
        return False

    if not Path(resume_path).exists():
        logger.error("Resume file not found: %s", resume_path)
        return False

    try:
        service = _authenticate()

        message = MIMEMultipart()
        message["To"] = job.recruiter_email
        message["Subject"] = f"Application: {job.title} at {job.company}"

        message.attach(MIMEText(cover_letter, "plain"))

        path = Path(resume_path)
        content_type, _ = mimetypes.guess_type(str(path))
        if content_type is None:
            content_type = "application/octet-stream"
        main_type, sub_type = content_type.split("/", 1)
        part = MIMEBase(main_type, sub_type)
        part.set_payload(path.read_bytes())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition", "attachment", filename=path.name
        )
        message.attach(part)

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(
            userId="me", body={"raw": raw}
        ).execute()

    except Exception:
        logger.exception("Failed to send email to %s", job.recruiter_email)
        return False

    return True
