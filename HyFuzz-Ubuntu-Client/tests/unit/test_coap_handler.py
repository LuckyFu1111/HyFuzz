from src.protocols.coap_handler import CoAPHandler
from src.models.execution_models import ExecutionRequest


def test_coap_handler_executes():
    handler = CoAPHandler()
    response = handler.execute(ExecutionRequest(payload_id="1", protocol="coap"))
    assert response["status"] == "ok"
