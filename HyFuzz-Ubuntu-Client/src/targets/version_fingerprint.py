"""Version fingerprinting."""
from __future__ import annotations


class VersionFingerprinter:
    def fingerprint(self, data: dict[str, str]) -> dict[str, str]:
        banner = data.get("banner", "unknown/0")
        service, _, version = banner.partition("/")
        return {"service": service, "version": version or "0"}


if __name__ == "__main__":
    fingerprinter = VersionFingerprinter()
    print(fingerprinter.fingerprint({"banner": "CoAP/1.0"}))
