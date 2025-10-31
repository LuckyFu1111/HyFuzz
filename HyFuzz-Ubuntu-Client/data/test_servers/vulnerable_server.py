"""Deliberately vulnerable server stub."""


def handle(message: str) -> str:
    if "overflow" in message:
        return "crash"
    return "safe"


if __name__ == "__main__":
    print(handle("overflow"))
