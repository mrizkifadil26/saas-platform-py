import asyncio
from collections.abc import Sequence

from .consumer import Consumer
from .lifecycle import Lifecycle


class Worker:
    def __init__(
        self,
        consumers: Sequence[Consumer],
        lifecycle: Lifecycle | None = None,
    ) -> None:
        self._consumers = list(consumers)
        self._lifecycle = lifecycle or Lifecycle()

    async def run(self) -> None:
        self._lifecycle.install_signal_handlers()

        for consumer in self._consumers:
            self._lifecycle.add_shutdown_callback(
                consumer.close,
            )

        tasks = [
            asyncio.create_task(
                consumer.run(),
                name=f"consumer:{type(consumer).__name__}",
            )
            for consumer in self._consumers
        ]

        try:
            await self._lifecycle.wait()
        finally:
            for task in tasks:
                task.cancel()

            await asyncio.gather(
                *tasks,
                return_exceptions=True,
            )

            await self._lifecycle.shutdown()
