"""Intercept signals."""
from __future__ import annotations

import signal
from typing import Dict


class SignalInterceptor:
    def __init__(self) -> None:
        self.intercepted: Dict[int, int] = {}

    def intercept(self, sig: int) -> None:
        self.intercepted[sig] = signal.getsignal(sig)
        signal.signal(sig, signal.SIG_IGN)


if __name__ == "__main__":
    interceptor = SignalInterceptor()
    interceptor.intercept(signal.SIGTERM)
    print(interceptor.intercepted)
