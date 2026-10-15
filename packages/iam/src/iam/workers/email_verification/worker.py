import asyncio

from iam.shared.application.messaging.consumer import MessageConsumer
from iam.workers.worker import StopSignal, Worker


class EmailVerificationWorker(Worker):
    def __init__(
        self,
        *,
        consumer: MessageConsumer,
        interval: float = 1.0,
    ) -> None:
        self._consumer = consumer
        self._interval = interval

    async def run(self, stop: StopSignal) -> None:
        while not stop.is_stopped:
            await self._consumer.consume(
                subject="iam.email_verification.requested",
                consumer_name="iam.email-verification",
            )

            try:
                await asyncio.wait_for(
                    stop.wait(),
                    timeout=self._interval,
                )
            except TimeoutError:
                # TOOD: handle exception later
                pass
