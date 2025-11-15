"""
Email Notifier

Sends notifications via email using SMTP.
Supports HTML emails, attachments, and TLS/SSL.

Author: HyFuzz Team
Version: 2.0.0
"""

from __future__ import annotations
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from dataclasses import dataclass
from .notification_models import NotificationMessage


@dataclass
class EmailConfig:
    """Configuration for Email notifications"""
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    from_address: str = "hyfuzz@example.com"
    use_tls: bool = True
    use_ssl: bool = False


class EmailNotifier:
    """Email Notifier for sending notifications via SMTP"""

    def __init__(self, config: Optional[EmailConfig] = None):
        self.config = config or EmailConfig()
        self.logger = logging.getLogger(__name__)

    def send(self, message: NotificationMessage, recipients: Optional[List[str]] = None) -> bool:
        """Send email notification"""
        if not recipients:
            recipients = [message.channel] if '@' in message.channel else []
        
        if not recipients:
            self.logger.info(f"[EMAIL] {message.subject}: {message.body}")
            return True

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.subject
            msg['From'] = self.config.from_address
            msg['To'] = ', '.join(recipients)

            # Plain text and HTML versions
            text_part = MIMEText(message.body, 'plain')
            html_part = MIMEText(f"<html><body><h2>{message.subject}</h2><p>{message.body}</p></body></html>", 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)

            # Connect and send
            if self.config.use_ssl:
                server = smtplib.SMTP_SSL(self.config.smtp_host, self.config.smtp_port)
            else:
                server = smtplib.SMTP(self.config.smtp_host, self.config.smtp_port)
                if self.config.use_tls:
                    server.starttls()

            if self.config.smtp_user and self.config.smtp_password:
                server.login(self.config.smtp_user, self.config.smtp_password)

            server.sendmail(self.config.from_address, recipients, msg.as_string())
            server.quit()

            self.logger.info(f"Email sent to {recipients}: {message.subject}")
            return True

        except Exception as e:
            self.logger.error(f"Email send failed: {e}")
            return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    notifier = EmailNotifier()
    msg = NotificationMessage(channel="test@example.com", subject="Test", body="Testing email notifier")
    notifier.send(msg)
