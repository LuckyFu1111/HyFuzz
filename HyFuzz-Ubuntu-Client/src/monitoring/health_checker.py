"""Health checking."""
from __future__ import annotations


class HealthChecker:
    def check(self) -> bool:
        return True


if __name__ == "__main__":
    checker = HealthChecker()
    print(checker.check())
