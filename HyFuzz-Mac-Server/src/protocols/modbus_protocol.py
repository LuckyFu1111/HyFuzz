"""Modbus protocol handler with basic state awareness."""

from __future__ import annotations

from typing import Any, Dict

from .base_protocol import BaseProtocolHandler, ProtocolContext, ProtocolSpec


class ModbusProtocolHandler(BaseProtocolHandler):
    name = "modbus"
    SPEC = ProtocolSpec(
        name="modbus",
        description="Modbus TCP/RTU fuzzing handler",
        stateful=True,
        default_parameters={"function_code": 3, "address": 0, "count": 1},
    )

    def prepare_request(self, context: ProtocolContext, payload: Dict[str, Any]) -> Dict[str, Any]:
        request = super().prepare_request(context, payload)
        request["payload"] = payload.get("payload", request["payload"])
        request["function_code"] = payload.get("function_code", 3)
        request["address"] = payload.get("address", 0)
        request["count"] = payload.get("count", 1)
        return request

    def validate(self, payload: Dict[str, Any]) -> bool:
        return "function_code" in payload


if __name__ == "__main__":
    handler = ModbusProtocolHandler()
    ctx = ProtocolContext(target="modbus://127.0.0.1:502")
    print(handler.prepare_request(ctx, {"function_code": 1, "address": 10, "count": 2}))
    print("Valid:", handler.validate({"function_code": 3}))
