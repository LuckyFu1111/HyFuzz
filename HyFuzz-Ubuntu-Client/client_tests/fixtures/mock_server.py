class MockServer:
    def send(self, payload: bytes) -> bytes:
        return payload
