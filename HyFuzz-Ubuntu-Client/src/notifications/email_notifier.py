"""Email notification backend."""
from __future__ import annotations

from .notification_models import Notification


class EmailNotifier:
    def send(self, message: str) -> Notification:
        notification = Notification(channel="email", message=message)
        print(f"Email sent: {message}")
        return notification


if __name__ == "__main__":
    notifier = EmailNotifier()
    notifier.send("hello")
