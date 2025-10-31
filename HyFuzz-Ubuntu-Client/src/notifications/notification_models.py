"""Notification models."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Notification:
    channel: str
    message: str


if __name__ == "__main__":
    print(Notification(channel="console", message="hello"))
