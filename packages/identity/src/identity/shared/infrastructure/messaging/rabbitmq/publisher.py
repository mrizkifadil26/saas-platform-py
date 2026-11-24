from dataclasses import dataclass

import aio_pika

from identity.shared.infrastructure.messaging.transport import TransportPublisher

from .client import RabbitMQClient


@dataclass(slots=True)
class RabbitMQTransportPublisher(TransportPublisher):
    client: RabbitMQClient

    async def publish(
        self,
        *,
        message_id: str,
        message_type: str,
        payload: bytes,
    ) -> None:
        message = aio_pika.Message(
            body=payload,
            message_id=message_id,
            type=message_type,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json",
        )

        await self.client.publish(
            message=message,
            routing_key=message_type,
        )
