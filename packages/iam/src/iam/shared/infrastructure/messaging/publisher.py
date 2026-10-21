from dataclasses import dataclass

from .message import Message
from .serializer import MessageSerializer
from .transport import TransportPublisher


@dataclass(slots=True)
class MessagePublisher:
    transport: TransportPublisher
    serializer: MessageSerializer

    async def publish(
        self,
        message: Message,
    ) -> None:
        body = self.serializer.serialize(message.payload)

        await self.transport.publish(
            # OutgoingMessage(
            #     subject=message.message_type,
            #     data=data,
            #     message_id=str(message.metadata.message_id),
            # )
            message_id=str(message.id),
            message_type=message.type,
            payload=body,
        )
