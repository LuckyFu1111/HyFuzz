"""Custom exceptions used across the client."""


class HyFuzzError(Exception):
    """Base exception for client errors."""


class ProtocolNotSupported(HyFuzzError):
    """Raised when an unsupported protocol is requested."""


class SandboxViolation(HyFuzzError):
    """Raised when payload execution attempts an unsafe action."""


if __name__ == "__main__":
    try:
        raise ProtocolNotSupported("demo")
    except ProtocolNotSupported as exc:
        print(f"Caught: {exc.__class__.__name__}")
