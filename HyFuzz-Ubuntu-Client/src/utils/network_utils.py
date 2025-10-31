"""Network utilities."""
from __future__ import annotations

import socket


def is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) == 0


if __name__ == "__main__":
    print("Port 80 open on localhost:", is_port_open("localhost", 80))
