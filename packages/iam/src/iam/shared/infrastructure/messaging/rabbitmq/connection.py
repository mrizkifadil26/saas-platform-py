from __future__ import annotations

import aio_pika
from aio_pika import RobustConnection

from .settings import RabbitMQSettings


class RabbitMQClient:
    def __init__(
        self,
        connection: RobustConnection,
    ) -> None:
        self._connection = connection

    @classmethod
    async def create(
        cls,
        settings: RabbitMQSettings,
    ) -> RabbitMQClient:
        connection = await aio_pika.connect_robust(settings.url)

        return cls(connection)

    @property
    def connection(self) -> RobustConnection:
        return self._connection

    async def health(self) -> None:
        if self._connection.is_closed:
            raise RuntimeError("RabbitMQ connection is closed")

    async def close(self) -> None:
        await self._connection.close()
