"""Generic mock server."""


def handle(message: str) -> str:
    return f"Handled {message}"


if __name__ == "__main__":
    print(handle("ping"))
