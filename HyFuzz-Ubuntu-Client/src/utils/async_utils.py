"""Async helpers."""
from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable


async def run_in_background(task: Callable[[], Awaitable[Any]]) -> asyncio.Task[Any]:
    loop = asyncio.get_running_loop()
    return loop.create_task(task())


if __name__ == "__main__":
    async def demo() -> int:
        await asyncio.sleep(0.01)
        return 1

    async def main() -> None:
        task = await run_in_background(demo)
        print(await task)

    asyncio.run(main())
