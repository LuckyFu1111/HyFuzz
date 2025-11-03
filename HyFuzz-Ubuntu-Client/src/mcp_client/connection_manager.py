"""HTTP connection manager for the HyFuzz MCP client."""
from __future__ import annotations

from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests
from requests import Response
from requests.exceptions import RequestException

DEFAULT_TIMEOUT = 5.0


class ConnectionManager:
    """Minimal HTTP client responsible for talking to the MCP server."""

    def __init__(self, endpoint: str, session: Optional[requests.Session] = None) -> None:
        self.endpoint = endpoint.rstrip("/")
        self._session = session or requests.Session()
        self._connected = False
        self._session_id: Optional[str] = None

    def connect(self, timeout: float = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """Perform a health probe followed by an ``initialize`` handshake."""

        health = self._session.get(self._url("health"), timeout=timeout)
        self._raise_for_status(health)

        self._connected = True
        initialise_message = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {},
            "id": "init",
        }
        try:
            response = self.send(initialise_message, timeout=timeout)
        except Exception:
            self._connected = False
            raise
        self._session_id = response.get("result", {}).get("sessionId")
        return response

    def send(self, message: Dict[str, Any], timeout: float = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        if not self._connected:
            raise RuntimeError("Not connected to MCP server")

        try:
            response = self._session.post(
                self._url("mcp/message"),
                json=message,
                timeout=timeout,
            )
            self._raise_for_status(response)
            return response.json()
        except ValueError as exc:
            raise RuntimeError("Invalid JSON response from MCP server") from exc
        except RequestException as exc:  # pragma: no cover - network failures
            raise RuntimeError(f"Failed to send MCP request: {exc}") from exc

    def is_connected(self) -> bool:
        return self._connected

    def _url(self, path: str) -> str:
        return urljoin(f"{self.endpoint}/", path)

    @staticmethod
    def _raise_for_status(response: Response) -> None:
        try:
            response.raise_for_status()
        except RequestException as exc:
            raise RuntimeError(f"MCP server returned HTTP {response.status_code}") from exc


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    manager = ConnectionManager("http://127.0.0.1:8000")
    try:
        handshake = manager.connect()
        print("Initialise response:", handshake)
    except Exception as error:  # noqa: BLE001
        print("Handshake failed:", error)
