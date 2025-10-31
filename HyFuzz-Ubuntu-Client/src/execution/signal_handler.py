"""Signal handling utilities."""
from __future__ import annotations

import signal
from typing import Any, Callable, Dict


class SignalHandler:
    def __init__(self) -> None:
        self._handlers: Dict[int, Callable[[int, Any], None]] = {}

    def register(self, sig: int, handler: Callable[[int, Any], None]) -> None:
        signal.signal(sig, handler)
        self._handlers[sig] = handler

    def registered(self) -> Dict[int, Callable[[int, Any], None]]:
        return dict(self._handlers)


if __name__ == "__main__":
    def demo(sig: int, _frame: Any) -> None:
        print("signal", sig)

    handler = SignalHandler()
    handler.register(signal.SIGINT, demo)
    print(handler.registered())
