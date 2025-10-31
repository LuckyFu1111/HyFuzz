"""MCP client entry point."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Dict

from .connection_manager import ConnectionManager
from .protocol_selector import ProtocolSelector
from .heartbeat_manager import HeartbeatManager
from ..utils.logger import get_logger


@dataclass
class ClientConfig:
    server_url: str
    protocols: list[str]


class MCPClient:
    """Lightweight MCP client capable of selecting execution protocols."""

    def __init__(self, config: ClientConfig) -> None:
        self.config = config
        self.logger = get_logger(__name__)
        self.connection_manager = ConnectionManager(config.server_url)
        self.selector = ProtocolSelector(config.protocols)
        self.heartbeat = HeartbeatManager()

    def connect(self) -> None:
        handshake = self.connection_manager.connect()
        protocol_version = handshake.get("result", {}).get("protocolVersion")
        self.logger.info(
            "Connected to %s (protocol=%s)",
            self.config.server_url,
            protocol_version,
        )
        self.heartbeat.record()

    def send_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        protocol = self.selector.choose(payload.get("protocol", "coap"))
        rpc_method = payload.get("rpc_method", "tools/call")
        request_id = str(payload.get("id", uuid.uuid4()))

        arguments = {k: v for k, v in payload.items() if k not in {"rpc_method", "id", "protocol"}}
        arguments["protocol"] = protocol

        if rpc_method == "tools/call":
            tool_name = arguments.pop("tool", f"{protocol}_fuzz")
            params: Dict[str, Any] = {"name": tool_name, "arguments": arguments}
        else:
            params = arguments

        message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": rpc_method,
            "params": params,
        }

        response = self.connection_manager.send(message)
        self.heartbeat.record()
        return response

    def is_alive(self) -> bool:
        return self.heartbeat.is_alive()


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    client = MCPClient(ClientConfig(server_url="http://127.0.0.1:8000", protocols=["coap", "modbus"]))
    client.connect()
    result = client.send_payload({"payload_id": "demo", "tool": "demo", "protocol": "coap"})
    print(result)
    print("Heartbeat alive:", client.is_alive())
