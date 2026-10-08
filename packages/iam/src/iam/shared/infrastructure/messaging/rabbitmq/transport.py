from typing import AsyncIterator

from aio_pika import Message

from iam.shared.application.messaging.transport import (
    OutgoingMessage,
    ReceivedMessage,
    TransportConsumer,
    TransportPublisher,
)
from iam.shared.infrastructure.messaging.rabbitmq.connection import RabbitMQConnection

from .message import RabbitMQReceivedMessage


class RabbitMQTransport(
    TransportPublisher,
    TransportConsumer,
):
    def __init__(self, connection: RabbitMQConnection) -> None:
        self._connection = connection

    async def consume(
        self,
        *,
        subject: str,
        consumer_name: str,
    ) -> AsyncIterator[ReceivedMessage]:
        channel = await self._connection.channel()

        exchange = await channel.declare_exchange(
            "messages",
            durable=True,
        )

        queue = await channel.declare_queue(consumer_name, durable=True)
        await queue.bind(
            exchange,
            routing_key=subject,
        )

        async with queue.iterator() as iterator:
            async for message in iterator:
                yield RabbitMQReceivedMessage(message)

    async def publish(self, message: OutgoingMessage) -> None:
        channel = await self._connection.channel()

        await channel.default_exchange.publish(
            Message(
                body=message.data,
                message_id=message.message_id,
                headers=dict(message.headers),
            ),
            routing_key=message.subject,
        )
