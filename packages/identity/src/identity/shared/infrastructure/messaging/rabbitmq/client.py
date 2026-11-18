from __future__ import annotations

from dataclasses import dataclass

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractExchange, AbstractQueue

from .settings import RabbitMQSettings


@dataclass(slots=True)
class RabbitMQClient:
    connection: AbstractConnection
    channel: AbstractChannel
    exchange: AbstractExchange

    @classmethod
    async def create(
        cls,
        settings: RabbitMQSettings,
        *,
        exchange_name: str,
    ) -> RabbitMQClient:
        connection = await aio_pika.connect_robust(settings.url)

        channel = await connection.channel()

        exchange = await channel.declare_exchange(
            exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )

        return cls(
            connection=connection,
            channel=channel,
            exchange=exchange,
        )

    async def declare_queue(
        self,
        name: str,
        *,
        durable: bool = True,
    ) -> AbstractQueue:
        return await self.channel.declare_queue(
            name,
            durable=durable,
        )

    async def bind_queue(
        self,
        queue: AbstractQueue,
        *,
        routing_key: str,
    ) -> None:
        await queue.bind(
            self.exchange,
            routing_key=routing_key,
        )

    async def publish(
        self,
        message: aio_pika.Message,
        *,
        routing_key: str,
    ) -> None:
        await self.exchange.publish(
            message,
            routing_key=routing_key,
        )

    async def health(self) -> None:
        if self.connection.is_closed:
            raise RuntimeError("RabbitMQ connection is closed")

    async def close(self) -> None:
        await self.connection.close()
