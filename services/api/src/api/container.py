from __future__ import annotations

from dataclasses import dataclass

from db import Database
from iam import Container as IAMContainer
from iam.shared.application.clock import Clock
from iam.shared.infrastructure.cache.redis import RedisClient
from iam.shared.infrastructure.messaging.rabbitmq import RabbitMQClient
from iam.shared.infrastructure.time.system_clock import SystemClock

from .settings import Settings


@dataclass(slots=True)
class AppContainer:
    settings: Settings

    app_db: Database
    rabbitmq: RabbitMQClient
    redis: RedisClient
    clock: Clock

    iam: IAMContainer

    @classmethod
    async def create(cls, settings: Settings) -> AppContainer:
        app_db = Database.create(settings.db)
        rabbitmq = await RabbitMQClient.create(settings.rabbitmq)
        redis = RedisClient.create(settings.redis)
        clock = SystemClock()

        return cls(
            settings=settings,
            app_db=app_db,
            rabbitmq=rabbitmq,
            redis=redis,
            clock=clock,
        )

    async def start(self) -> None: ...

    async def stop(self) -> None:
        await self.redis.close()
        await self.rabbitmq.close()
        await self.app_db.stop()
