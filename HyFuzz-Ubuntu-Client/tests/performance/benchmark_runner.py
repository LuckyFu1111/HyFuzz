from time import perf_counter

from src.execution.orchestrator import Orchestrator
from src.execution.utils import build_requests


def run_benchmark(iterations: int = 5) -> float:
    orchestrator = Orchestrator()
    orchestrator.queue_requests(build_requests([str(i) for i in range(iterations)], "coap"))
    start = perf_counter()
    orchestrator.run()
    return perf_counter() - start


if __name__ == "__main__":
    print(run_benchmark())
