"""
SMS Notifier

Sends SMS notifications via Twilio API.
Supports international numbers and delivery tracking.

Author: HyFuzz Team
Version: 2.0.0
"""

from __future__ import annotations
import logging
from typing import Optional, List
from dataclasses import dataclass
import aiohttp
from .notification_models import NotificationMessage


@dataclass
class SMSConfig:
    """Configuration for SMS notifications"""
    account_sid: Optional[str] = None
    auth_token: Optional[str] = None
    from_number: str = "+1234567890"
    twilio_api_url: str = "https://api.twilio.com/2010-04-01"


class SMSNotifier:
    """SMS Notifier using Twilio API"""

    def __init__(self, config: Optional[SMSConfig] = None):
        self.config = config or SMSConfig()
        self.logger = logging.getLogger(__name__)
        
        if not self.config.account_sid or not self.config.auth_token:
            self.logger.warning("No Twilio credentials provided.")

    async def send(self, message: NotificationMessage, phone_numbers: Optional[List[str]] = None) -> bool:
        """Send SMS notification"""
        if not phone_numbers:
            phone_numbers = [message.channel] if message.channel.startswith('+') else []
        
        if not phone_numbers or not self.config.account_sid:
            self.logger.info(f"[SMS] {message.subject}: {message.body}")
            return True

        url = f"{self.config.twilio_api_url}/Accounts/{self.config.account_sid}/Messages.json"
        auth = aiohttp.BasicAuth(self.config.account_sid, self.config.auth_token)

        try:
            async with aiohttp.ClientSession() as session:
                for phone in phone_numbers:
                    data = {
                        'From': self.config.from_number,
                        'To': phone,
                        'Body': f"{message.subject}: {message.body[:150]}"  # SMS limit
                    }
                    
                    async with session.post(url, data=data, auth=auth, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 201:
                            self.logger.info(f"SMS sent to {phone}")
                        else:
                            error = await response.text()
                            self.logger.error(f"SMS failed for {phone}: {error}")
            
            return True

        except Exception as e:
            self.logger.error(f"SMS send failed: {e}")
            return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    notifier = SMSNotifier()
    import asyncio
    msg = NotificationMessage(channel="+1234567890", subject="Alert", body="Test SMS")
    asyncio.run(notifier.send(msg))
