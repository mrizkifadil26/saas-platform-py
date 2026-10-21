from collections.abc import AsyncIterator
from dataclasses import dataclass

from aio_pika.abc import AbstractQueue

from iam.shared.infrastructure.messaging.message import ReceivedMessage
from iam.shared.infrastructure.messaging.rabbitmq.client import RabbitMQClient
from iam.shared.infrastructure.messaging.rabbitmq.delivery import from_rabbitmq
from iam.shared.infrastructure.messaging.serializer import MessageSerializer
from iam.shared.infrastructure.messaging.transport import TransportConsumer


@dataclass(slots=True)
class RabbitMQTransportConsumer(
    TransportConsumer,
):
    client: RabbitMQClient
    queue: AbstractQueue
    serializer: MessageSerializer

    def consume(self) -> AsyncIterator[ReceivedMessage]:
        return self._consume()

    async def _consume(
        self,
    ) -> AsyncIterator[ReceivedMessage]:
        async with self.queue.iterator() as iterator:
            async for message in iterator:
                yield from_rabbitmq(
                    message,
                    self.serializer,
                )
