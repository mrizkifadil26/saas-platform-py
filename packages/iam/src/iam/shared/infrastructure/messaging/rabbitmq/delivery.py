from uuid import UUID

from aio_pika.abc import AbstractIncomingMessage

from iam.shared.infrastructure.messaging.message import Message, MessageDelivery, ReceivedMessage
from iam.shared.infrastructure.messaging.serializer import MessageSerializer


class RabbitMQDelivery(MessageDelivery):
    def __init__(
        self,
        message: AbstractIncomingMessage,
    ) -> None:
        self._message = message

    async def ack(self) -> None:
        await self._message.ack()

    async def reject(
        self,
        *,
        requeue: bool = False,
    ) -> None:
        await self._message.reject(
            requeue=requeue,
        )


def from_rabbitmq(
    message: AbstractIncomingMessage,
    serializer: MessageSerializer,
) -> ReceivedMessage:
    if message.message_id is None:
        raise ValueError("RabbitMQ message has no message_id")

    if message.type is None:
        raise ValueError("RabbitMQ message has no message type")

    payload = serializer.deserialize(message.body)

    logical_message = Message(
        id=UUID(message.message_id),
        type=message.type,
        payload=payload,
    )

    return ReceivedMessage(
        message=logical_message,
        delivery=RabbitMQDelivery(message),
    )
