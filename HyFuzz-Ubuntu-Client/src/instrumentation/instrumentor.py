"""High-level instrumentor."""
from __future__ import annotations

from .ptrace_handler import PtraceHandler
from .coverage_tracker import CoverageTracker
from .syscall_monitor import SyscallMonitor
from .instrumentation_models import TraceEvent


class Instrumentor:
    def __init__(self) -> None:
        self.ptrace = PtraceHandler()
        self.coverage = CoverageTracker()
        self.syscalls = SyscallMonitor()

    def start(self, pid: int) -> None:
        self.ptrace.attach(pid)
        self.coverage.reset()
        self.syscalls.reset()

    def stop(self, pid: int) -> list[TraceEvent]:
        self.ptrace.detach(pid)
        return self.syscalls.events


if __name__ == "__main__":
    instrumentor = Instrumentor()
    instrumentor.start(1234)
    print(instrumentor.stop(1234))
