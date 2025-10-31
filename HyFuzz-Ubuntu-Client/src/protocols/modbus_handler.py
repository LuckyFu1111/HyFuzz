"""Modbus protocol handler."""
from __future__ import annotations

from typing import Dict

from .base_handler import BaseProtocolHandler
from ..models.execution_models import ExecutionRequest


class ModbusHandler(BaseProtocolHandler):
    name = "modbus"

    def execute(self, request: ExecutionRequest) -> Dict[str, str]:
        return {"status": "ok", "message": f"Modbus payload {request.payload_id}"}


if __name__ == "__main__":
    print(ModbusHandler().execute(ExecutionRequest(payload_id="1", protocol="modbus")))
