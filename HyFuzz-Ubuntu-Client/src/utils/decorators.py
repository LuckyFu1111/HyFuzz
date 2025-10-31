"""Decorator utilities."""
from __future__ import annotations

import functools
import time
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def timed(func: F) -> F:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        print(f"{func.__name__} took {duration:.6f}s")
        return result

    return wrapper  # type: ignore[return-value]


if __name__ == "__main__":
    @timed
    def demo() -> None:
        time.sleep(0.01)

    demo()
