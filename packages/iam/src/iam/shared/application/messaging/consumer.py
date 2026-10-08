from typing import Any

from .handler import MessageHandler
from .serializer import MessageSerializer
from .transport import TransportConsumer


class MessageConsumer:
    def __init__(
        self,
        *,
        transport: TransportConsumer,
        serializer: MessageSerializer,
        handler: MessageHandler[Any],
        retry_delay: float = 5.0,
    ) -> None:
        self._transport = transport
        self._serializer = serializer
        self._handler = handler
        self._retry_delay = retry_delay

    async def consume(
        self,
        *,
        subject: str,
        consumer_name: str,
    ) -> None:
        async for message in self._transport.consume(
            subject=subject,
            consumer_name=consumer_name,
        ):
            envelope = self._serializer.deserialize(message.data)

            try:
                await self._handler(envelope)
            except Exception:
                await message.retry(self._retry_delay)
            else:
                await message.ack()
