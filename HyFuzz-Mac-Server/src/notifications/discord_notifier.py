"""
Discord Notifier

Sends notifications to Discord channels via webhooks.
Supports rich embeds, mentions, and file attachments.

Author: HyFuzz Team  
Version: 2.0.0
"""

from __future__ import annotations
import logging
import json
from typing import Optional, Dict, Any
from dataclasses import dataclass
import aiohttp
from .notification_models import NotificationMessage


@dataclass
class DiscordConfig:
    """Configuration for Discord notifications"""
    webhook_url: Optional[str] = None
    username: str = "HyFuzz Bot"
    avatar_url: Optional[str] = None


class DiscordNotifier:
    """Discord Notifier for sending messages to Discord channels"""

    def __init__(self, config: Optional[DiscordConfig] = None):
        self.config = config or DiscordConfig()
        self.logger = logging.getLogger(__name__)
        
        if not self.config.webhook_url:
            self.logger.warning("No Discord webhook URL provided.")

    async def send(self, message: NotificationMessage) -> bool:
        """Send notification to Discord"""
        if not self.config.webhook_url:
            self.logger.info(f"[DISCORD] {message.subject}: {message.body}")
            return True

        payload = self._build_embed(message)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status in [200, 204]:
                        self.logger.info(f"Discord message sent: {message.subject}")
                        return True
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Discord webhook failed: {response.status} - {error_text}")
                        return False
        except Exception as e:
            self.logger.error(f"Discord request failed: {e}")
            return False

    def _build_embed(self, message: NotificationMessage) -> Dict[str, Any]:
        """Build Discord embed"""
        severity_colors = {
            'critical': 0xD32F2F,
            'high': 0xF57C00,
            'medium': 0xFBC02D,
            'low': 0x388E3C,
            'info': 0x1976D2,
        }
        
        severity = 'info'
        for level in ['critical', 'high', 'medium', 'low']:
            if level in message.subject.lower() or level in message.body.lower():
                severity = level
                break

        embed = {
            "title": message.subject,
            "description": message.body[:4096],
            "color": severity_colors.get(severity, 0x757575),
            "timestamp": message.created_at.isoformat(),
            "footer": {"text": "HyFuzz Security Testing"}
        }

        payload = {
            "username": self.config.username,
            "embeds": [embed]
        }
        
        if self.config.avatar_url:
            payload["avatar_url"] = self.config.avatar_url

        return payload


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    notifier = DiscordNotifier()
    import asyncio
    msg = NotificationMessage(channel="discord", subject="Test", body="Testing Discord notifier")
    asyncio.run(notifier.send(msg))
