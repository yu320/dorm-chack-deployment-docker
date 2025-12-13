# backend/app/services/notification_service.py
import os
import html
import logging
from typing import List, Optional, Dict, Any, Union
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import asyncio
import smtplib
import time

from jinja2 import Environment, FileSystemLoader

from ..config import settings
from .. import crud
from ..database import AsyncSessionLocal

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        # 設定 Jinja2 環境
        # 假設 templates 資料夾位於 backend/app/templates
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))

    async def _get_email_config(self) -> Dict[str, Any]:
        """
        Fetch email configuration from database, fallback to settings.
        """
        config = {
            "MAIL_SERVER": settings.MAIL_SERVER,
            "MAIL_PORT": settings.MAIL_PORT,
            "MAIL_USERNAME": settings.MAIL_USERNAME,
            "MAIL_PASSWORD": settings.MAIL_PASSWORD,
            "MAIL_FROM": settings.MAIL_FROM,
            "MAIL_TLS": settings.MAIL_TLS,
            "MAIL_SSL": settings.MAIL_SSL,
        }

        # Try to fetch from DB
        try:
            async with AsyncSessionLocal() as db:
                server = await crud.crud_system_setting.get_by_key(db, "mail_server")
                if server and server.value: config["MAIL_SERVER"] = server.value
                
                port = await crud.crud_system_setting.get_by_key(db, "mail_port")
                if port and port.value: config["MAIL_PORT"] = int(port.value)
                
                username = await crud.crud_system_setting.get_by_key(db, "mail_username")
                if username and username.value: config["MAIL_USERNAME"] = username.value
                
                password = await crud.crud_system_setting.get_by_key(db, "mail_password")
                if password and password.value: config["MAIL_PASSWORD"] = password.value
                
                sender = await crud.crud_system_setting.get_by_key(db, "mail_from")
                if sender and sender.value: config["MAIL_FROM"] = sender.value

                tls = await crud.crud_system_setting.get_by_key(db, "mail_tls")
                if tls and tls.value: config["MAIL_TLS"] = tls.value.lower() == "true"
                
                ssl = await crud.crud_system_setting.get_by_key(db, "mail_ssl")
                if ssl and ssl.value: config["MAIL_SSL"] = ssl.value.lower() == "true"
                
        except Exception as e:
            logger.error(f"Failed to fetch email config from DB: {e}")
        
        return config

    def _send_bulk_emails_sync(
        self,
        config: Dict[str, Any],
        recipients: List[str],
        messages: List[Union[str, MIMEMultipart]]
    ):
        """
        Synchronous function to send emails.
        """
        try:
            with smtplib.SMTP(config["MAIL_SERVER"], config["MAIL_PORT"]) as server:
                if config["MAIL_TLS"]:
                    server.starttls()
                server.login(config["MAIL_USERNAME"], config["MAIL_PASSWORD"])
                logger.info(f"SMTP Connection established. Starting batch send for {len(recipients)} emails.")

                for i, recipient_email in enumerate(recipients):
                    try:
                        # If message is MIMEMultipart, convert to string
                        msg_content = messages[i].as_string() if isinstance(messages[i], MIMEMultipart) else messages[i]
                        server.sendmail(config["MAIL_FROM"], recipient_email, msg_content)
                        logger.info(f"Email sent successfully to {recipient_email}")
                        time.sleep(1.5) 
                    except Exception as e:
                        logger.error(f"Failed to send to {recipient_email}: {e}")
        except Exception as connection_error:
            logger.error(f"SMTP Connection failed: {connection_error}")

    async def send_email_notification(
        self,
        recipients: List[str],
        subject: str,
        body_html: str,
        attachments: Optional[List[dict]] = None
    ) -> None:
        """
        發送電子郵件通知，支援 HTML 內容和附件。
        """
        config = await self._get_email_config()

        if not config["MAIL_USERNAME"] or not config["MAIL_PASSWORD"] or not config["MAIL_FROM"] or not config["MAIL_SERVER"]:
            logger.warning("Email sending is not configured (DB or Settings). Skipping email.")
            return

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = config["MAIL_FROM"]
        # message["To"] should be set per individual email if sending bulk individually, 
        # but here we are preparing one message object.
        # Ideally, we should set "To" header inside the loop or not set it if using BCC style?
        # Standard practice: "To" header matches the envelope recipient or is generic.
        # Here we just set it to the list join for simplicity, or we can clone the message.
        message["To"] = ", ".join(recipients)

        # HTML 內容
        html_part = MIMEText(body_html, "html")
        message.attach(html_part)

        # 處理附件
        if attachments:
            for attachment_data in attachments:
                filename = attachment_data.get("filename")
                content = attachment_data.get("content")
                if filename and content:
                    part = MIMEApplication(content, Name=filename)
                    part["Content-Disposition"] = f'attachment; filename="{filename}"'
                    message.attach(part)
        
        # Send using the updated logic
        await asyncio.to_thread(
            self._send_bulk_emails_sync,
            config,
            recipients,
            [message] * len(recipients)
        )

    async def send_password_reset_email(self, to_email: str, username: str, reset_link: str, lang: str = "en") -> None:
        if lang not in ["en", "zh"]: lang = "en"
        subjects = {
            "en": "Password Reset Request for Student Dormitory Inspection System",
            "zh": "學生宿舍檢查系統 - 重設密碼請求"
        }
        subject = subjects.get(lang, subjects["en"])
        template = self.env.get_template(f'email/{lang}/password_reset.html')
        body_html = template.render(username=username, reset_link=reset_link)
        await self.send_email_notification(recipients=[to_email], subject=subject, body_html=body_html)

    async def send_verification_email(self, to_email: str, username: str, verification_link: str, lang: str = "en") -> None:
        if lang not in ["en", "zh"]: lang = "en"
        subjects = {
            "en": "Verify Your Account - Student Dormitory Inspection System",
            "zh": "驗證您的帳戶 - 學生宿舍檢查系統"
        }
        subject = subjects.get(lang, subjects["en"])
        template = self.env.get_template(f'email/{lang}/verification_email.html')
        body_html = template.render(username=username, verification_link=verification_link)
        await self.send_email_notification(recipients=[to_email], subject=subject, body_html=body_html)

    async def send_welcome_email(self, to_email: str, username: str, lang: str = "en") -> None:
        if lang not in ["en", "zh"]: lang = "en"
        subjects = {
            "en": "Welcome to Student Dormitory Inspection System",
            "zh": "歡迎加入學生宿舍檢查系統"
        }
        subject = subjects.get(lang, subjects["en"])
        template = self.env.get_template(f'email/{lang}/welcome.html')
        body_html = template.render(username=username)
        await self.send_email_notification(recipients=[to_email], subject=subject, body_html=body_html)

    async def send_inspection_report_email(
        self,
        to_email: str,
        student_name: str,
        room_number: str,
        pdf_content: bytes,
        filename: str,
        lang: str = "en"
    ) -> None:
        if lang not in ["en", "zh"]: lang = "en"
        subjects = {
            "en": f"Inspection Report for {student_name} - Room {room_number}",
            "zh": f"檢查報告 - {student_name} (寢室 {room_number})"
        }
        subject = subjects.get(lang, subjects["en"])
        template = self.env.get_template(f'email/{lang}/inspection_report.html')
        body_html = template.render(recipient_email=to_email, student_name=student_name, room_number=room_number)
        await self.send_email_notification(
            recipients=[to_email],
            subject=subject,
            body_html=body_html,
            attachments=[{"filename": filename, "content": pdf_content}]
        )

notification_service = NotificationService()