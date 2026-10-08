from typing import Any, Protocol

from .message import MessageEnvelope
from .serializer import MessageSerializer
from .transport import OutgoingMessage, TransportPublisher


class MessagePublisher(Protocol):
    async def publish(
        self,
        message: MessageEnvelope[Any],
    ) -> None: ...


class DefaultMessagePublisher:
    def __init__(
        self,
        *,
        transport: TransportPublisher,
        serializer: MessageSerializer,
    ) -> None:
        self._transport = transport
        self._serializer = serializer

    async def publish(self, message: MessageEnvelope[Any]) -> None:
        data = self._serializer.serialize(message)

        await self._transport.publish(
            OutgoingMessage(
                subject=message.message_type,
                data=data,
                message_id=str(message.metadata.message_id),
            )
        )
