"""Sandbox manager."""
from __future__ import annotations

from ..utils.exceptions import SandboxViolation


class SandboxManager:
    def __init__(self, allow_network: bool = False) -> None:
        self.allow_network = allow_network

    def validate(self, command: str) -> None:
        if not self.allow_network and "curl" in command:
            raise SandboxViolation("Network access is disabled")


if __name__ == "__main__":
    sandbox = SandboxManager()
    try:
        sandbox.validate("curl http://example.com")
    except SandboxViolation as exc:
        print("Sandbox blocked:", exc)
