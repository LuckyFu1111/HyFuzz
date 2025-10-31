"""Time helpers."""
from __future__ import annotations

import datetime as _dt


def utc_now() -> _dt.datetime:
    return _dt.datetime.now(tz=_dt.timezone.utc)


if __name__ == "__main__":
    print("UTC now:", utc_now())
