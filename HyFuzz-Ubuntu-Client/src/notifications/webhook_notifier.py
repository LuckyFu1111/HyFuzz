"""Webhook notifications."""
from __future__ import annotations

from .notification_models import Notification


class WebhookNotifier:
    def send(self, message: str) -> Notification:
        notification = Notification(channel="webhook", message=message)
        print(f"Webhook sent: {message}")
        return notification


if __name__ == "__main__":
    notifier = WebhookNotifier()
    notifier.send("hello")
