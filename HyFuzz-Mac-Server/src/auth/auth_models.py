"""Authentication models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe


@dataclass
class User:
    username: str
    password_hash: str


@dataclass
class SessionToken:
    token: str
    username: str
    expires_at: datetime

    @classmethod
    def create(cls, username: str, ttl_seconds: int = 3600) -> "SessionToken":
        expiry = datetime.now(UTC) + timedelta(seconds=ttl_seconds)
        return cls(token=token_urlsafe(16), username=username, expires_at=expiry)

    def is_expired(self) -> bool:
        return datetime.now(UTC) >= self.expires_at


if __name__ == "__main__":
    token = SessionToken.create("demo")
    print(token, token.is_expired())
