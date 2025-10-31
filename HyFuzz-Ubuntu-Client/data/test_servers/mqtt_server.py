"""MQTT test server stub."""


def handle(message: str) -> str:
    return f"MQTT handled {message}"


if __name__ == "__main__":
    print(handle("publish"))
