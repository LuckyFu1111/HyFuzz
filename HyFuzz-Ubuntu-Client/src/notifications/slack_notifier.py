"""Slack notifications."""
from __future__ import annotations

from .notification_models import Notification


class SlackNotifier:
    def send(self, message: str) -> Notification:
        notification = Notification(channel="slack", message=message)
        print(f"Slack sent: {message}")
        return notification


if __name__ == "__main__":
    notifier = SlackNotifier()
    notifier.send("hello")
