from src.mcp_client.client import MCPClient, ClientConfig


def test_client_heartbeat_and_protocol_selection():
    client = MCPClient(ClientConfig(server_url="http://localhost", protocols=["coap", "modbus"]))
    client.connect()
    response = client.send_payload({"payload_id": "test", "protocol": "coap"})
    assert response["endpoint"] == "http://localhost"
    assert client.is_alive()
