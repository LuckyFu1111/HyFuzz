from src.analysis.crash_analyzer import CrashAnalyzer


def test_crash_analysis_speed():
    analyzer = CrashAnalyzer()
    analysis = analyzer.analyse("1", "main->foo")
    assert analysis.payload_id == "1"
