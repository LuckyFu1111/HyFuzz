from src.judge.metrics_calculator import MetricsCalculator


def test_metrics_calculator_success():
    calculator = MetricsCalculator()
    assert calculator.calculate({"status": "ok"}) == 1.0
