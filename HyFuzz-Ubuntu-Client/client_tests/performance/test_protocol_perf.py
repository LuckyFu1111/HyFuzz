from src.protocols.protocol_factory import get_handler
from src.models.execution_models import ExecutionRequest


def test_protocol_factory_latency():
    handler = get_handler("coap")
    response = handler.execute(ExecutionRequest(payload_id="1", protocol="coap"))
    assert response["status"] == "ok"
