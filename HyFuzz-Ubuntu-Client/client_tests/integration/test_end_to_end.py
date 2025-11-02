import json

from src.mcp_client.client import MCPClient, ClientConfig
from src.execution.orchestrator import Orchestrator
from src.execution.utils import build_requests


def test_end_to_end_flow():
    client = MCPClient(ClientConfig(server_url="http://localhost", protocols=["coap"]))
    client.connect()
    orchestrator = Orchestrator()
    orchestrator.queue_requests(build_requests(["1"], "coap"))
    results = orchestrator.run()
    response = client.send_payload({"payload_id": "1", "protocol": "coap"})
    ack_payload = json.loads(response["ack"])
    assert results[0].payload_id == ack_payload["payload_id"]
