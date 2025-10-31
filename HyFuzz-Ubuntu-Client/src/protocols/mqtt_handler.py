"""MQTT protocol handler."""
from __future__ import annotations

from typing import Dict

from .base_handler import BaseProtocolHandler
from ..models.execution_models import ExecutionRequest


class MQTTHandler(BaseProtocolHandler):
    name = "mqtt"

    def execute(self, request: ExecutionRequest) -> Dict[str, str]:
        return {"status": "ok", "message": f"MQTT payload {request.payload_id}"}


if __name__ == "__main__":
    print(MQTTHandler().execute(ExecutionRequest(payload_id="1", protocol="mqtt")))
