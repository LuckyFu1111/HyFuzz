"""Protocol selection logic."""
from __future__ import annotations

from typing import List

from ..utils.validators import ensure_supported


class ProtocolSelector:
    def __init__(self, supported: List[str]) -> None:
        self.supported = supported

    def choose(self, requested: str) -> str:
        return ensure_supported(requested, self.supported)


if __name__ == "__main__":
    selector = ProtocolSelector(["coap", "modbus"])
    print(selector.choose("coap"))
