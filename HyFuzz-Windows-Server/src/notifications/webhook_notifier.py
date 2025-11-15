"""
Webhook Notifier

Sends notifications to generic webhooks.
Supports custom payloads and headers.

Author: HyFuzz Team
Version: 2.0.0
"""

from __future__ import annotations
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
import aiohttp
from .notification_models import NotificationMessage


@dataclass
class WebhookConfig:
    """Configuration for Webhook notifications"""
    url: Optional[str] = None
    method: str = "POST"
    headers: Dict[str, str] = field(default_factory=dict)
    custom_payload_template: Optional[Dict[str, Any]] = None


class WebhookNotifier:
    """Generic Webhook Notifier"""

    def __init__(self, config: Optional[WebhookConfig] = None):
        self.config = config or WebhookConfig()
        self.logger = logging.getLogger(__name__)
        
        if not self.config.url:
            self.logger.warning("No webhook URL provided.")

    async def send(self, message: NotificationMessage) -> bool:
        """Send notification to webhook"""
        if not self.config.url:
            self.logger.info(f"[WEBHOOK] {message.subject}: {message.body}")
            return True

        payload = self._build_payload(message)
        headers = {"Content-Type": "application/json", **self.config.headers}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    self.config.method,
                    self.config.url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if 200 <= response.status < 300:
                        self.logger.info(f"Webhook notification sent: {message.subject}")
                        return True
                    else:
                        error = await response.text()
                        self.logger.error(f"Webhook failed: {response.status} - {error}")
                        return False
        except Exception as e:
            self.logger.error(f"Webhook request failed: {e}")
            return False

    def _build_payload(self, message: NotificationMessage) -> Dict[str, Any]:
        """Build webhook payload"""
        if self.config.custom_payload_template:
            return self.config.custom_payload_template

        return {
            "channel": message.channel,
            "subject": message.subject,
            "body": message.body,
            "timestamp": message.created_at.isoformat(),
            "source": "HyFuzz"
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    notifier = WebhookNotifier()
    import asyncio
    msg = NotificationMessage(channel="webhook", subject="Test", body="Testing webhook notifier")
    asyncio.run(notifier.send(msg))
