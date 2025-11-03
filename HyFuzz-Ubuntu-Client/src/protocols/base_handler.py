"""Base protocol handler."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict

from ..models.execution_models import ExecutionRequest


@dataclass(frozen=True)
class ProtocolCapabilities:
    """Describe the client-side expectations for a protocol handler."""

    name: str
    description: str = ""
    stateful: bool = False
    default_parameters: Dict[str, str] = field(default_factory=dict)


class BaseProtocolHandler(ABC):
    name: str
    capabilities = ProtocolCapabilities(name="base", description="Base protocol handler")

    @abstractmethod
    def execute(self, request: ExecutionRequest) -> Dict[str, str]:
        raise NotImplementedError

    def execute_stateful(self, request: ExecutionRequest, session: "ProtocolSessionState") -> Dict[str, str]:
        """Execute a stateful request. Defaults to stateless execution."""

        return self.execute(request)

    def get_capabilities(self) -> ProtocolCapabilities:
        if self.capabilities.name == "base":
            return ProtocolCapabilities(name=self.name)
        return self.capabilities


if __name__ == "__main__":
    class Demo(BaseProtocolHandler):
        name = "demo"

        def execute(self, request: ExecutionRequest) -> Dict[str, str]:
            return {"status": "ok", "message": request.payload_id}

    print(Demo().execute(ExecutionRequest(payload_id="1", protocol="demo")))
