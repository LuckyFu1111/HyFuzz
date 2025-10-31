"""Notification dispatcher."""
from __future__ import annotations

from typing import Iterable

from .notification_models import Notification


class Notifier:
    def send(self, notifications: Iterable[Notification]) -> None:
        for notification in notifications:
            print(f"[{notification.channel}] {notification.message}")


if __name__ == "__main__":
    notifier = Notifier()
    notifier.send([Notification(channel="console", message="hello")])
