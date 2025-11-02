from pathlib import Path
import json


def load_json(name: str) -> dict:
    path = Path("data") / name
    return json.loads(path.read_text(encoding="utf-8"))
