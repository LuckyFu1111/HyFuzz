"""Simple retry logic."""
from __future__ import annotations

import time
from typing import Callable, TypeVar

T = TypeVar("T")


def retry(func: Callable[[], T], attempts: int = 3, delay: float = 0.1) -> T:
    last_error: Exception | None = None
    for _ in range(attempts):
        try:
            return func()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(delay)
    raise last_error if last_error else RuntimeError("retry failed")


if __name__ == "__main__":
    counter = {"value": 0}

    def flaky() -> str:
        counter["value"] += 1
        if counter["value"] < 2:
            raise ValueError("fail")
        return "ok"

    print(retry(flaky))
