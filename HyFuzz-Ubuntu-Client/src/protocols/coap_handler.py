"""CoAP protocol handler."""
from __future__ import annotations

from typing import Dict

from .base_handler import BaseProtocolHandler
from ..models.execution_models import ExecutionRequest


class CoAPHandler(BaseProtocolHandler):
    name = "coap"

    def execute(self, request: ExecutionRequest) -> Dict[str, str]:
        method = request.parameters.get("method", "GET").upper()
        path = request.parameters.get("path", "/")
        confirmable = request.parameters.get("confirmable", "True")
        is_confirmable = str(confirmable).lower() in {"true", "1", "yes"}
        allowed_methods = {"GET", "POST", "PUT", "DELETE"}
        success = method in allowed_methods and not path.endswith("forbidden")
        status = "ok" if success else "error"
        mode = "confirmable" if is_confirmable else "non-confirmable"
        message = f"CoAP {method} {path} ({mode}) -> {request.payload_id}"
        if not success:
            message += " rejected"
        return {"status": status, "message": message}


if __name__ == "__main__":
    sample = ExecutionRequest(
        payload_id="1",
        protocol="coap",
        parameters={"method": "GET", "path": "/demo", "confirmable": "true"},
    )
    print(CoAPHandler().execute(sample))
