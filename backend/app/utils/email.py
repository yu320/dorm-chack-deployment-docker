import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase # Import MIMEBase for attachments
from email.header import Header
from ..config import settings
import asyncio
from typing import List, Union # Add Union for MIMEMultipart
import html # Import html for escaping
import logging

logger = logging.getLogger(__name__)

def _send_bulk_emails_with_reuse(
    mail_server, mail_port, mail_tls, mail_username, mail_password,
    mail_from: str, recipients: List[str], messages: List[Union[str, MIMEMultipart]]
):
    """
    Sends multiple emails using a single SMTP connection with delays.
    'messages' now expects a list of MIMEText (as string) or MIMEMultipart objects.
    """
    try:
        with smtplib.SMTP(mail_server, mail_port) as server:
            if mail_tls:
                server.starttls()
            server.login(mail_username, mail_password)
            logger.info(f"SMTP Connection established. Starting batch send for {len(recipients)} emails.")

            for i, recipient_email in enumerate(recipients):
                try:
                    # If message is MIMEMultipart, convert to string
                    msg_content = messages[i].as_string() if isinstance(messages[i], MIMEMultipart) else messages[i]
                    server.sendmail(mail_from, recipient_email, msg_content)
                    logger.info(f"Email sent successfully to {recipient_email}")
                    # Add a delay to avoid being flagged as spam
                    time.sleep(1.5) # Always sleep after sending, even the last one
                except Exception as e:
                    logger.error(f"Failed to send to {recipient_email}: {e}")
    except Exception as connection_error:
        logger.error(f"SMTP Connection failed: {connection_error}")

async def send_email(
    recipients: List[str],
    message: MIMEMultipart # Now accepts a MIMEMultipart object directly
):
    """
    Sends a pre-constructed MIMEMultipart email using a single, persistent SMTP connection.
    """
    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD or not settings.MAIL_FROM or not settings.MAIL_SERVER:
        logger.warning("Email sending is not configured. Skipping email.")
        return

    # 2. Send them in a single batch using one connection in a separate thread
    await asyncio.to_thread(
        _send_bulk_emails_with_reuse,
        settings.MAIL_SERVER,
        settings.MAIL_PORT,
        settings.MAIL_TLS,
        settings.MAIL_USERNAME,
        settings.MAIL_PASSWORD,
        settings.MAIL_FROM,
        recipients,
        [message] * len(recipients) # Pass the same MIMEMultipart message for all recipients
    )


