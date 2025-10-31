from src.instrumentation.instrumentor import Instrumentor


def test_instrumentor_collects_syscalls():
    instrumentor = Instrumentor()
    instrumentor.start(123)
    instrumentor.syscalls.record("open", {"file": "demo"})
    events = instrumentor.stop(123)
    assert events
