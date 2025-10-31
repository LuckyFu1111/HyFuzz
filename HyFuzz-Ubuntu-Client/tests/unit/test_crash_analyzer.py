from src.analysis.crash_analyzer import CrashAnalyzer


def test_crash_analyzer_returns_frames():
    analyzer = CrashAnalyzer()
    analysis = analyzer.analyse("1", "main->foo")
    assert analysis.stack_trace
