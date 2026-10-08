from __future__ import annotations

from dataclasses import dataclass

from db import Database
from iam.context import IAMContext
from iam.shared.infrastructure.cache.redis import RedisClient
from iam.shared.infrastructure.messaging.rabbitmq import RabbitMQClient
from iam.shared.infrastructure.time.system_clock import SystemClock

from .settings import Settings


@dataclass(slots=True)
class Infrastructure:
    app_db: Database
    rabbitmq: RabbitMQClient
    redis: RedisClient


@dataclass(slots=True)
class AppContainer:
    settings: Settings
    infrastructure: Infrastructure

    iam: IAMContext

    @classmethod
    async def create(cls, settings: Settings) -> AppContainer:
        app_db = Database.create(settings.db)
        rabbitmq = await RabbitMQClient.create(settings.rabbitmq)
        redis = RedisClient.create(settings.redis)
        clock = SystemClock()

        return cls(
            settings=settings,
            infrastructure=Infrastructure(
                app_db=app_db,
                rabbitmq=rabbitmq,
                redis=redis,
            ),
            iam=IAMContext.create(
                db=app_db,
                redis=redis,
                clock=clock,
                # settings=settings,
            ),
        )

    async def start(self) -> None:
        ...
        # await self.iam.start()

    async def stop(self) -> None:
        # await self.iam.stop()

        # await self.infrastructure.redis.aclose()
        await self.infrastructure.redis.close()
        await self.infrastructure.rabbitmq.close()
        await self.infrastructure.app_db.stop()
