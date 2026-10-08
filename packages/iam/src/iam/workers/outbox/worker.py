import asyncio

from iam.shared.application.messaging.outbox.publisher import OutboxPublisher
from iam.workers.worker import StopSignal, Worker


class OutboxWorker(Worker):
    def __init__(
        self,
        *,
        publisher: OutboxPublisher,
        interval: float = 1.0,
        batch_size: int = 100,
    ) -> None:
        self._publisher = publisher
        self._interval = interval
        self._batch_size = batch_size

    async def run(self, stop: StopSignal) -> None:
        while not stop.is_stopped:
            await self._publisher.publish(limit=self._batch_size)

            try:
                await asyncio.wait_for(
                    stop.wait(),
                    timeout=self._interval,
                )
            except TimeoutError:
                # TOOD: handle exception later
                pass
