"""MCP client entry point."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .connection_manager import ConnectionManager
from .protocol_selector import ProtocolSelector
from .heartbeat_manager import HeartbeatManager
from .utils import serialize_message
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
        self.connection_manager.connect()
        self.logger.info("Connected to server %s", self.config.server_url)

    def send_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        protocol = self.selector.choose(payload.get("protocol", "coap"))
        payload["protocol"] = protocol
        message = serialize_message(payload)
        response = self.connection_manager.send(message)
        self.heartbeat.record()
        return response

    def is_alive(self) -> bool:
        return self.heartbeat.is_alive()


if __name__ == "__main__":
    client = MCPClient(ClientConfig(server_url="http://localhost:8000", protocols=["coap", "modbus"]))
    client.connect()
    print(client.send_payload({"payload_id": "demo", "protocol": "coap"}))
    print("Heartbeat alive:", client.is_alive())
