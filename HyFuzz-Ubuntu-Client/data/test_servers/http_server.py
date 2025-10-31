"""HTTP test server stub."""


def handle(message: str) -> str:
    return f"HTTP handled {message}"


if __name__ == "__main__":
    print(handle("GET /"))
