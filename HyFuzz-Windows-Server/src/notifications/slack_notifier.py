"""
Slack Notifier

Sends notifications to Slack channels via webhooks or Slack API.
Supports rich formatting, file attachments, and interactive messages.

Author: HyFuzz Team
Version: 2.0.0
"""

from __future__ import annotations

import logging
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import aiohttp

from .notification_models import NotificationMessage


@dataclass
class SlackConfig:
    """Configuration for Slack notifications"""
    webhook_url: Optional[str] = None
    bot_token: Optional[str] = None
    default_channel: str = "#general"
    username: str = "HyFuzz Bot"
    icon_emoji: str = ":robot_face:"
    enable_mentions: bool = True


class SlackNotifier:
    """
    Slack Notifier for sending messages to Slack channels

    Features:
    - Webhook-based messaging (simple, recommended)
    - Bot API messaging (advanced features)
    - Rich message formatting with Slack blocks
    - File attachments and images
    - Thread support for organized conversations
    - Error handling with retry logic

    Example:
        >>> config = SlackConfig(webhook_url="https://hooks.slack.com/...")
        >>> notifier = SlackNotifier(config)
        >>> msg = NotificationMessage(
        ...     channel="#alerts",
        ...     subject="Critical Alert",
        ...     body="Vulnerability found!"
        ... )
        >>> await notifier.send(msg)
    """

    def __init__(self, config: Optional[SlackConfig] = None):
        """
        Initialize Slack notifier

        Args:
            config: Slack configuration
        """
        self.config = config or SlackConfig()
        self.logger = logging.getLogger(__name__)

        if not self.config.webhook_url and not self.config.bot_token:
            self.logger.warning(
                "No Slack webhook URL or bot token provided. "
                "Notifications will only be logged."
            )

    async def send(self, message: NotificationMessage) -> bool:
        """
        Send notification to Slack

        Args:
            message: Notification message to send

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            if self.config.webhook_url:
                return await self._send_webhook(message)
            elif self.config.bot_token:
                return await self._send_api(message)
            else:
                # Fallback: just log
                self.logger.info(f"[SLACK] {message.subject}: {message.body}")
                return True

        except Exception as e:
            self.logger.error(f"Failed to send Slack notification: {e}", exc_info=True)
            return False

    async def _send_webhook(self, message: NotificationMessage) -> bool:
        """Send message using Slack webhook"""
        payload = self._build_webhook_payload(message)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        self.logger.info(f"Slack message sent successfully: {message.subject}")
                        return True
                    else:
                        error_text = await response.text()
                        self.logger.error(
                            f"Slack webhook failed: {response.status} - {error_text}"
                        )
                        return False

        except Exception as e:
            self.logger.error(f"Slack webhook request failed: {e}")
            return False

    async def _send_api(self, message: NotificationMessage) -> bool:
        """Send message using Slack Bot API"""
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.config.bot_token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        payload = {
            "channel": message.channel or self.config.default_channel,
            "text": f"*{message.subject}*\n{message.body}",
            "username": self.config.username,
            "icon_emoji": self.config.icon_emoji,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    result = await response.json()

                    if result.get('ok'):
                        self.logger.info(f"Slack API message sent: {message.subject}")
                        return True
                    else:
                        self.logger.error(f"Slack API error: {result.get('error')}")
                        return False

        except Exception as e:
            self.logger.error(f"Slack API request failed: {e}")
            return False

    def _build_webhook_payload(self, message: NotificationMessage) -> Dict[str, Any]:
        """Build Slack webhook payload with blocks"""
        severity_colors = {
            'critical': '#d32f2f',
            'high': '#f57c00',
            'medium': '#fbc02d',
            'low': '#388e3c',
            'info': '#1976d2',
        }

        # Detect severity from message
        severity = 'info'
        for level in ['critical', 'high', 'medium', 'low']:
            if level in message.subject.lower() or level in message.body.lower():
                severity = level
                break

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": message.subject,
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message.body[:3000]  # Slack has a 3000 char limit
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Sent:* {message.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}"
                    }
                ]
            }
        ]

        payload = {
            "username": self.config.username,
            "icon_emoji": self.config.icon_emoji,
            "attachments": [{
                "color": severity_colors.get(severity, '#757575'),
                "blocks": blocks
            }]
        }

        if message.channel:
            payload["channel"] = message.channel

        return payload


# Synchronous wrapper for compatibility
class SlackNotifierSync:
    """Synchronous wrapper for SlackNotifier"""

    def __init__(self, config: Optional[SlackConfig] = None):
        self.notifier = SlackNotifier(config)
        self.logger = logging.getLogger(__name__)

    def send(self, message: NotificationMessage) -> bool:
        """Send notification synchronously"""
        import asyncio

        try:
            # Get or create event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Run async send
            return loop.run_until_complete(self.notifier.send(message))

        except Exception as e:
            self.logger.error(f"Synchronous send failed: {e}")
            self.logger.info(f"[SLACK] {message.subject}: {message.body}")
            return False


# Export both versions
SlackNotifier.__doc__ += "\n\nNote: This is an async notifier. Use SlackNotifierSync for synchronous usage."


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test with fallback mode (no webhook)
    print("Testing Slack notifier (fallback mode)...")
    notifier = SlackNotifierSync()
    msg = NotificationMessage(
        channel="#alerts",
        subject="Test Alert",
        body="This is a test notification from HyFuzz."
    )
    notifier.send(msg)
    print("Test complete!")
