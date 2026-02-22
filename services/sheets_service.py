"""Google Sheets API service wrapper.

Setup:
    1. Enable the Google Sheets API in Google Cloud Console.
    2. Use the same OAuth credentials.json as Gmail (or a separate one).
    3. Set the SHEETS_SPREADSHEET_ID environment variable to the target
       spreadsheet ID (the long string in the spreadsheet URL).
    4. On first run, authorize Sheets access when prompted.

Schema (Sheet1, columns A-G):
    A: Job Title
    B: Company
    C: Match Score
    D: Contact Status
    E: Action
    F: Email Sent
    G: Reason
"""

import logging
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import config
from models import TrackerEntry

logger = logging.getLogger(__name__)

_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _authenticate():
    """Build and return an authenticated Sheets API service."""
    creds = None
    token_path = Path(config.SHEETS_TOKEN_PATH)
    creds_path = Path(config.SHEETS_CREDENTIALS_PATH)

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

    return build("sheets", "v4", credentials=creds)


def append_row(entry: TrackerEntry) -> None:
    """Append a tracker entry as a new row to Sheet1.

    Args:
        entry: TrackerEntry to log.
    """
    service = _authenticate()
    row = [
        entry.job_title,
        entry.company,
        entry.match_score,
        entry.contact_status.value,
        entry.action.value,
        entry.email_sent,
        entry.reason,
    ]
    service.spreadsheets().values().append(
        spreadsheetId=config.SHEETS_SPREADSHEET_ID,
        range="Sheet1!A:G",
        valueInputOption="RAW",
        body={"values": [row]},
    ).execute()


def update_status(row_index: int, status: str) -> None:
    """Update the action column (E) for a specific row.

    Args:
        row_index: 1-based row number in the spreadsheet.
        status: New status value to write.
    """
    service = _authenticate()
    service.spreadsheets().values().update(
        spreadsheetId=config.SHEETS_SPREADSHEET_ID,
        range=f"Sheet1!E{row_index}",
        valueInputOption="RAW",
        body={"values": [[status]]},
    ).execute()
