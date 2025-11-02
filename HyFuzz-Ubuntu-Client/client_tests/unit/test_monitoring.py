from src.monitoring.metrics_collector import MetricsCollector


def test_metrics_collector_returns_metrics():
    collector = MetricsCollector()
    metrics = collector.collect()
    assert "cpu_percent" in metrics
