import asyncio
import importlib.util
import sys
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[3]
SERVER_ROOT = ROOT / "HyFuzz-Windows-Server"
CLIENT_ROOT = ROOT / "HyFuzz-Ubuntu-Client"

if str(CLIENT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(CLIENT_ROOT / "src"))


def _load_server_module(module: str) -> object:
    module_path = SERVER_ROOT / "src" / Path(module.replace(".", "/") + ".py")
    spec = importlib.util.spec_from_file_location(module, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module {module} from {module_path}")
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded



pkg_spec = importlib.util.spec_from_file_location('mcp_server', SERVER_ROOT / 'src' / 'mcp_server' / '__init__.py')
if pkg_spec and pkg_spec.loader:
    pkg_module = importlib.util.module_from_spec(pkg_spec)
    pkg_spec.loader.exec_module(pkg_module)
    pkg_module.__path__ = [str((SERVER_ROOT / 'src' / 'mcp_server').resolve())]
    sys.modules.setdefault('mcp_server', pkg_module)

_server = _load_server_module("mcp_server.server")
MCPServer = getattr(_server, "MCPServer")
ServerConfig = getattr(_server, "ServerConfig")

from src.mcp_client.client import MCPClient, ClientConfig  # noqa: E402


def test_client_can_execute_tool_via_http() -> None:
    async def runner() -> None:
        server_config = ServerConfig(
            host="127.0.0.1",
            port=0,
            transports=["http"],
            stdio_enabled=False,
            http_enabled=True,
            websocket_enabled=False,
        )
        server = MCPServer(server_config)
        await server.start()
        try:
            http_transport = server.transports["http"]
            sockets = http_transport.site._server.sockets  # type: ignore[attr-defined]
            port = sockets[0].getsockname()[1]

            client = MCPClient(
                ClientConfig(
                    server_url=f"http://127.0.0.1:{port}",
                    protocols=["coap", "modbus"],
                )
            )

            def run_client() -> Dict[str, Any]:
                client.connect()
                time.sleep(0.7)
                return client.send_payload({"payload_id": "demo", "protocol": "coap", "tool": "demo"})

            response = await asyncio.to_thread(run_client)
            assert response["jsonrpc"] == "2.0"
            outer = response.get("result", {})
            inner = outer.get("result", {})
            assert inner.get("name") == "demo"
            assert client.is_alive()
        finally:
            await server.stop()

    asyncio.run(runner())
