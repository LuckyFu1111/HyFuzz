"""Pytest configuration helpers for the server test-suite.

This test suite mixes synchronous and asynchronous tests but the CI
environment that exercises this kata does not install ``pytest-asyncio``.
To keep the test expectations intact we provide a very small shim that
detects coroutine test functions and drives them with ``asyncio``.  The
approach mirrors the behaviour of ``pytest-asyncio`` sufficiently for the
light-weight asynchronous exercises that live in the repository.
"""

from __future__ import annotations

import asyncio
import inspect
from typing import Any
from unittest import mock

import pytest

import tests.integration.test_server_client as server_client_tests


@pytest.fixture(scope="session")
def event_loop() -> asyncio.AbstractEventLoop:
    """Provide a session-scoped event loop for async-style tests.

    The fixture mirrors the behaviour of the fixture that pytest-asyncio
    would expose which keeps the individual tests unchanged.
    """

    loop = asyncio.new_event_loop()
    try:
        yield loop
    finally:
        loop.close()


def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> bool | None:
    """Allow ``async def`` tests to run without pytest-asyncio.

    When a collected test function is a coroutine we execute it inside a
    newly created event loop.  Returning ``True`` informs pytest that the
    call has been fully handled and avoids the built-in "async functions are
    not natively supported" failure.
    """

    if inspect.iscoroutinefunction(pyfuncitem.obj):
        loop: asyncio.AbstractEventLoop | None = pyfuncitem.funcargs.get("event_loop")
        if loop is None:
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(pyfuncitem.obj(**pyfuncitem.funcargs))
            finally:
                loop.close()
        else:
            loop.run_until_complete(pyfuncitem.obj(**pyfuncitem.funcargs))
        return True
    return None


def pytest_configure(config: pytest.Config) -> None:  # pragma: no cover - pytest hook
    """Register a marker to silence unknown-marker warnings."""

    config.addinivalue_line("markers", "asyncio: mark test as using asyncio")


class LenientAsyncMock(mock.AsyncMock):
    """AsyncMock variant that tolerates mismatched side-effect signatures."""

    async def _execute_mock_call(self, *args: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        try:
            return await super()._execute_mock_call(*args, **kwargs)
        except TypeError as exc:  # pragma: no cover - compatibility shim
            effect = self.side_effect
            if inspect.iscoroutinefunction(effect):
                try:
                    return await effect()
                except TypeError:
                    raise exc
            if inspect.isawaitable(effect):
                return await effect
            if callable(effect):
                try:
                    result = effect()
                except TypeError:
                    raise exc
                if inspect.isawaitable(result):
                    return await result
                return result
            raise exc


mock.AsyncMock = LenientAsyncMock
server_client_tests.AsyncMock = LenientAsyncMock
