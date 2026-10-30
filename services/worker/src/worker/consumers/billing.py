from worker.runtime import Consumer

from identity.shared.infrastructure.messaging.consumer import MessageConsumer


class BillingConsumer(Consumer):
    def __init__(
        self,
        messages: MessageConsumer,
        handler: BillingHandler,
    ) -> None:
        super().__init__()

        self._messages = messages
        self._handler = handler

    async def consume(self) -> None:
        async for message in self._messages.consume(
            subject="",
            consumer="",
        ):
            if self._stop.is_set():
                break

            await self._handler.handle(message)
