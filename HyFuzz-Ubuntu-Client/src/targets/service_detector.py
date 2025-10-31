"""Detect services running on a target."""
from __future__ import annotations

from typing import Dict


class ServiceDetector:
    def detect(self, banner: str) -> Dict[str, str]:
        return {"service": banner.split("/")[0], "version": banner.split("/")[1] if "/" in banner else "unknown"}


if __name__ == "__main__":
    detector = ServiceDetector()
    print(detector.detect("CoAP/1.0"))
