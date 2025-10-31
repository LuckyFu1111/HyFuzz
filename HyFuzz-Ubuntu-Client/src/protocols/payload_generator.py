"""Generate protocol payloads."""
from __future__ import annotations

from typing import Dict

from ..models.execution_models import ExecutionRequest


def build_payload(request: ExecutionRequest) -> Dict[str, str]:
    return {"payload_id": request.payload_id, "protocol": request.protocol}


if __name__ == "__main__":
    from ..models.execution_models import ExecutionRequest

    print(build_payload(ExecutionRequest(payload_id="1", protocol="coap")))
