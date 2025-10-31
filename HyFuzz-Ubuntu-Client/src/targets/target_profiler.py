"""Profiles discovered targets."""
from __future__ import annotations

from .target_models import TargetProfile


class TargetProfiler:
    def profile(self, target: dict[str, object]) -> TargetProfile:
        return TargetProfile(
            host=str(target.get("host", "localhost")),
            port=int(target.get("port", 0)),
            protocol=str(target.get("protocol", "coap")),
            service=str(target.get("service", "unknown")),
        )


if __name__ == "__main__":
    profiler = TargetProfiler()
    print(profiler.profile({"host": "localhost", "port": 5683, "protocol": "coap", "service": "CoAP"}))
