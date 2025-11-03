"""Data models for notifications."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class NotificationMessage:
    channel: str
    subject: str
    body: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


if __name__ == "__main__":
    print(NotificationMessage(channel="console", subject="Demo", body="Test"))
