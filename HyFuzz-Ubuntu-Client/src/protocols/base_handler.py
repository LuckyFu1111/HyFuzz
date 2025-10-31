"""Base protocol handler."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict

from ..models.execution_models import ExecutionRequest


class BaseProtocolHandler(ABC):
    name: str

    @abstractmethod
    def execute(self, request: ExecutionRequest) -> Dict[str, str]:
        raise NotImplementedError


if __name__ == "__main__":
    class Demo(BaseProtocolHandler):
        name = "demo"

        def execute(self, request: ExecutionRequest) -> Dict[str, str]:
            return {"status": "ok", "message": request.payload_id}

    print(Demo().execute(ExecutionRequest(payload_id="1", protocol="demo")))
