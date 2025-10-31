from src.instrumentation.instrumentor import Instrumentor


def test_instrumentation_overhead_small():
    instrumentor = Instrumentor()
    instrumentor.start(1)
    instrumentor.syscalls.record("open", {"file": "demo"})
    events = instrumentor.stop(1)
    assert len(events) == 1
