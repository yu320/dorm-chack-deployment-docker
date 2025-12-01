# backend/app/services/notification_service.py
import os
import html
from typing import List, Optional
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, FileSystemLoader

from ..config import settings
from ..utils.email import send_email as send_email_util # 避免循環引用

class NotificationService:
    def __init__(self):
        # 設定 Jinja2 環境
        # 假設 templates 資料夾位於 backend/app/templates
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))

    async def send_email_notification(
        self,
        recipients: List[str],
        subject: str,
        body_html: str,
        attachments: Optional[List[dict]] = None # [{"filename": "report.pdf", "content": b"PDF_CONTENT"}]
    ) -> None:
        """
        發送電子郵件通知，支援 HTML 內容和附件。
        """
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = settings.MAIL_FROM
        message["To"] = ", ".join(recipients)

        # HTML 內容
        html_part = MIMEText(body_html, "html")
        message.attach(html_part)

        # 處理附件
        if attachments:
            for attachment_data in attachments:
                filename = attachment_data.get("filename")
                content = attachment_data.get("content") # 預期為 bytes
                if filename and content:
                    part = MIMEApplication(content, Name=filename)
                    part["Content-Disposition"] = f'attachment; filename="{filename}"'
                    message.attach(part)
        
        await send_email_util(recipients, message)

    async def send_password_reset_email(self, to_email: str, username: str, reset_link: str, lang: str = "en") -> None:
        """
        發送忘記密碼重設郵件 (使用 Jinja2 模板)
        """
        # 簡單的語言 fallback 機制
        if lang not in ["en", "zh"]:
            lang = "en"
            
        subjects = {
            "en": "Password Reset Request for Student Dormitory Inspection System",
            "zh": "學生宿舍檢查系統 - 重設密碼請求"
        }
        subject = subjects.get(lang, subjects["en"])
        
        template_path = f'email/{lang}/password_reset.html'
        template = self.env.get_template(template_path)
        body_html = template.render(username=username, reset_link=reset_link)
        
        await self.send_email_notification(recipients=[to_email], subject=subject, body_html=body_html)

    async def send_verification_email(self, to_email: str, username: str, verification_link: str, lang: str = "en") -> None:
        """
        發送帳戶驗證郵件
        """
        if lang not in ["en", "zh"]:
            lang = "en"

        subjects = {
            "en": "Verify Your Account - Student Dormitory Inspection System",
            "zh": "驗證您的帳戶 - 學生宿舍檢查系統"
        }
        subject = subjects.get(lang, subjects["en"])

        template_path = f'email/{lang}/verification_email.html'
        template = self.env.get_template(template_path)
        body_html = template.render(username=username, verification_link=verification_link)

        await self.send_email_notification(recipients=[to_email], subject=subject, body_html=body_html)

    async def send_welcome_email(self, to_email: str, username: str, lang: str = "en") -> None:
        """
        發送註冊成功歡迎信 (使用 Jinja2 模板)
        """
        # 簡單的語言 fallback 機制
        if lang not in ["en", "zh"]:
            lang = "en"

        subjects = {
            "en": "Welcome to Student Dormitory Inspection System",
            "zh": "歡迎加入學生宿舍檢查系統"
        }
        subject = subjects.get(lang, subjects["en"])
        
        template_path = f'email/{lang}/welcome.html'
        template = self.env.get_template(template_path)
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
        """
        發送檢查報告郵件 (含 PDF 附件)
        """
        # 簡單的語言 fallback 機制
        if lang not in ["en", "zh"]:
            lang = "en"

        subjects = {
            "en": f"Inspection Report for {student_name} - Room {room_number}",
            "zh": f"檢查報告 - {student_name} (寢室 {room_number})"
        }
        subject = subjects.get(lang, subjects["en"])

        template_path = f'email/{lang}/inspection_report.html'
        template = self.env.get_template(template_path)
        body_html = template.render(recipient_email=to_email, student_name=student_name, room_number=room_number)

        await self.send_email_notification(
            recipients=[to_email],
            subject=subject,
            body_html=body_html,
            attachments=[
                {
                    "filename": filename,
                    "content": pdf_content
                }
            ]
        )

# 創建一個服務實例，以便在其他地方重複使用
notification_service = NotificationService()
