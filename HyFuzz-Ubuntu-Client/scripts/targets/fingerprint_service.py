#!/usr/bin/env python3
"""Generate service fingerprints."""
from src.targets.version_fingerprint import VersionFingerprinter

if __name__ == "__main__":
    fingerprinter = VersionFingerprinter()
    print(fingerprinter.fingerprint({"banner": "CoAP/1.0"}))
