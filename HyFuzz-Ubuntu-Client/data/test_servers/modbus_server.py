"""Simple Modbus test server stub."""


def handle(message: str) -> str:
    return f"Modbus response to {message}"


if __name__ == "__main__":
    print(handle("ping"))
