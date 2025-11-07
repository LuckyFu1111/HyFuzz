from pathlib import Path


def test_dashboard_static_files_exist() -> None:
    base = Path(__file__).resolve().parents[2] / 'src' / 'dashboard' / 'static'
    assert (base / 'js' / 'main.js').exists()
