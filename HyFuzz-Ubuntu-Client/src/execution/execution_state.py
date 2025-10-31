"""Execution state management."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ExecutionState:
    status: str = "ready"

    @classmethod
    def current(cls) -> "ExecutionState":
        return cls()


if __name__ == "__main__":
    print(ExecutionState.current())
