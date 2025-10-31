"""Prioritise tasks."""
from __future__ import annotations

from typing import Iterable, List, Tuple


class TaskPrioritizer:
    def prioritise(self, tasks: Iterable[Tuple[str, int]]) -> List[str]:
        return [task for task, _ in sorted(tasks, key=lambda item: item[1], reverse=True)]


if __name__ == "__main__":
    prioritizer = TaskPrioritizer()
    print(prioritizer.prioritise([("a", 1), ("b", 3)]))
