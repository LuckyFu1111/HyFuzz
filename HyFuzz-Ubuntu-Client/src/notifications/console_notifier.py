"""Console notifier."""
from __future__ import annotations

from .notification_models import Notification


class ConsoleNotifier:
    def send(self, message: str) -> Notification:
        notification = Notification(channel="console", message=message)
        print(f"Console: {message}")
        return notification


if __name__ == "__main__":
    notifier = ConsoleNotifier()
    notifier.send("hello")
