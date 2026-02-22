import os

MIN_MATCH_SCORE: int = 75

TELEGRAM_BOT_TOKEN: str = os.environ.get("TELEGRAM_BOT_TOKEN", "")

GMAIL_CREDENTIALS_PATH: str = "credentials.json"
GMAIL_TOKEN_PATH: str = "gmail_token.json"

SHEETS_SPREADSHEET_ID: str = os.environ.get("SHEETS_SPREADSHEET_ID", "")
SHEETS_CREDENTIALS_PATH: str = "credentials.json"
SHEETS_TOKEN_PATH: str = "sheets_token.json"

MASTER_RESUME_PATH: str = "data/master_resume.txt"
COVER_LETTER_TEMPLATE_PATH: str = "data/cover_letter_template.txt"
EMAIL_INPUT_PATH: str = "data/email_input.txt"
RESUME_PDF_PATH: str = "Abhik_Hore_Resume_2026.pdf"
