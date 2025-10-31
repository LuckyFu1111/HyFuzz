"""Balance load across workers."""
from __future__ import annotations

from typing import Dict


class LoadBalancer:
    def assign(self, workers: Dict[str, int]) -> str:
        return min(workers, key=workers.get)


if __name__ == "__main__":
    balancer = LoadBalancer()
    print(balancer.assign({"worker1": 2, "worker2": 1}))
