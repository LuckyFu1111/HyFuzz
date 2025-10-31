"""Interpret signals from executions."""
from __future__ import annotations


class SignalInterpreter:
    def interpret(self, signal_code: int) -> str:
        mapping = {11: "SIGSEGV", 6: "SIGABRT"}
        return mapping.get(signal_code, "UNKNOWN")


if __name__ == "__main__":
    interpreter = SignalInterpreter()
    print(interpreter.interpret(11))
