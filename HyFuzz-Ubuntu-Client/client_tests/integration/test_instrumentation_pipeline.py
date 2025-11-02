from src.instrumentation.instrumentor import Instrumentor


def test_instrumentation_pipeline_records_events():
    instrumentor = Instrumentor()
    instrumentor.start(1)
    instrumentor.syscalls.record("open", {"file": "demo"})
    events = instrumentor.stop(1)
    assert events[0].name == "open"
