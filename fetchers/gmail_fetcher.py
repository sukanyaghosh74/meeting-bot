import os
import logging
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("meeting-prep-bot")

async def fetch_gmail_emails(meeting_name):
    """
    Fetch recent emails from Gmail/IMAP filtered by meeting_name (subject or body).
    Returns a string summary of relevant emails.
    """
    user = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_PASSWORD")
    imap_server = "imap.gmail.com"
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(user, password)
        mail.select("inbox")
        # Search for emails containing the meeting_name in subject or body
        status, messages = mail.search(None, f'(BODY "{meeting_name}")')
        email_ids = messages[0].split()[-5:]  # Get up to 5 most recent
        summaries = []
        for eid in email_ids:
            _, msg_data = mail.fetch(eid, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8", errors="ignore")
                    from_ = msg.get("From")
                    summaries.append(f"From: {from_}\nSubject: {subject}")
        mail.logout()
        if not summaries:
            return "No relevant emails found."
        return "\n".join(summaries)
    except Exception as e:
        logger.error(f"Gmail fetch error: {e}")
        return "[Error fetching emails]"
