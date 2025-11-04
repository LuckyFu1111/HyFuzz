import pytest
from src.mcp_client.client import MCPClient, ClientConfig


@pytest.mark.skip(reason="Requires live server - use for manual integration testing")
def test_client_server_roundtrip():
    client = MCPClient(ClientConfig(server_url="http://localhost", protocols=["coap"]))
    client.connect()
    response = client.send_payload({"payload_id": "demo", "protocol": "coap"})
    assert response["endpoint"] == "http://localhost"
