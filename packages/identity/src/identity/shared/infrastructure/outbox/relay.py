import asyncio
from dataclasses import dataclass
from datetime import timedelta

from identity.shared.infrastructure.outbox.publisher import OutboxPublisher, PublishBatchResult
from identity.shared.infrastructure.time.clock import Clock


@dataclass(slots=True)
class OutboxRelay:
    publisher: OutboxPublisher
    clock: Clock
    batch_size: int = 100
    lease_duration: timedelta = timedelta(minutes=2)
    poll_interval: float = 1.0

    def __post_init__(
        self,
    ) -> None:
        if self.batch_size <= 0:
            raise ValueError("batch_size must be greater than zero")

        if self.lease_duration <= timedelta():
            raise ValueError("lease_duration must be greater than zero")

        if self.poll_interval < 0:
            raise ValueError("poll_interval cannot be negative")

    async def run_once(self) -> PublishBatchResult:
        now = self.clock.now()
        lease_until = now + self.lease_duration

        return await self.publisher.publish_batch(
            limit=self.batch_size,
            locked_until=lease_until,
        )

    async def run_forever(
        self,
        stop_event: asyncio.Event,
    ) -> None:
        while not stop_event.is_set():
            result = await self.run_once()

            if result.claimed == 0:
                try:
                    await asyncio.wait_for(
                        stop_event.wait(),
                        timeout=self.poll_interval,
                    )
                except asyncio.TimeoutError:
                    pass
