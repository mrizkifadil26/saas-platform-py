from __future__ import annotations

import asyncio
from typing import Protocol, Sequence


class Worker(Protocol):
    async def run(self, stop: StopSignal) -> None: ...


class WorkerGroup:
    def __init__(self, workers: Sequence[Worker]) -> None:
        self._workers = workers
        self._stop = StopSignal()

    async def run(self) -> None:
        tasks = [
            asyncio.create_task(worker.run(self._stop)) for worker in self._workers
        ]

        try:
            await asyncio.gather(*tasks)
        finally:
            self._stop.stop()
            await asyncio.gather(*tasks, return_exceptions=True)

    def stop(self) -> None:
        self._stop.stop()


class StopSignal:
    def __init__(self) -> None:
        self._event = asyncio.Event()

    def stop(self) -> None:
        self._event.set()

    @property
    def is_stopped(self) -> bool:
        return self._event.is_set()

    async def wait(self) -> None:
        await self._event.wait()
