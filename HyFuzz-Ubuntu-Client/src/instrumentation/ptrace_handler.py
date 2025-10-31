"""Stub ptrace handler."""
from __future__ import annotations

from typing import List


class PtraceHandler:
    def __init__(self) -> None:
        self.attached: List[int] = []

    def attach(self, pid: int) -> None:
        self.attached.append(pid)

    def detach(self, pid: int) -> None:
        if pid in self.attached:
            self.attached.remove(pid)


if __name__ == "__main__":
    handler = PtraceHandler()
    handler.attach(1)
    handler.detach(1)
    print(handler.attached)
