"""
Teams Notifier

Sends notifications to Microsoft Teams channels via webhooks.
Supports adaptive cards and rich formatting.

Author: HyFuzz Team
Version: 2.0.0
"""

from __future__ import annotations
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
import aiohttp
from .notification_models import NotificationMessage


@dataclass
class TeamsConfig:
    """Configuration for Teams notifications"""
    webhook_url: Optional[str] = None


class TeamsNotifier:
    """Microsoft Teams Notifier"""

    def __init__(self, config: Optional[TeamsConfig] = None):
        self.config = config or TeamsConfig()
        self.logger = logging.getLogger(__name__)
        
        if not self.config.webhook_url:
            self.logger.warning("No Teams webhook URL provided.")

    async def send(self, message: NotificationMessage) -> bool:
        """Send notification to Teams"""
        if not self.config.webhook_url:
            self.logger.info(f"[TEAMS] {message.subject}: {message.body}")
            return True

        payload = self._build_adaptive_card(message)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        self.logger.info(f"Teams message sent: {message.subject}")
                        return True
                    else:
                        error = await response.text()
                        self.logger.error(f"Teams webhook failed: {response.status} - {error}")
                        return False
        except Exception as e:
            self.logger.error(f"Teams request failed: {e}")
            return False

    def _build_adaptive_card(self, message: NotificationMessage) -> Dict[str, Any]:
        """Build Teams adaptive card"""
        severity_colors = {
            'critical': 'attention',
            'high': 'warning',
            'medium': 'accent',
            'low': 'good',
            'info': 'default',
        }
        
        severity = 'info'
        for level in ['critical', 'high', 'medium', 'low']:
            if level in message.subject.lower() or level in message.body.lower():
                severity = level
                break

        return {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": message.subject,
            "themeColor": severity_colors.get(severity, 'default'),
            "title": message.subject,
            "text": message.body,
            "sections": [{
                "activityTitle": "HyFuzz Security Testing",
                "activitySubtitle": message.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')
            }]
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    notifier = TeamsNotifier()
    import asyncio
    msg = NotificationMessage(channel="teams", subject="Test", body="Testing Teams notifier")
    asyncio.run(notifier.send(msg))
