"""Simple CoAP test server stub."""


def handle(message: str) -> str:
    return f"CoAP response to {message}"


if __name__ == "__main__":
    print(handle("ping"))
