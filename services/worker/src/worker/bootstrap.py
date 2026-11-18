from __future__ import annotations

from dataclasses import dataclass

from db import Database
from identity.shared.infrastructure.messaging.rabbitmq import RabbitMQClient
from worker.runtime.worker import Worker

from .settings import Settings, get_settings


@dataclass(slots=True)
class Container:
    settings: Settings
    db: Database
    rabbitmq: RabbitMQClient

    @classmethod
    def create(
        cls,
        *,
        settings: Settings | None = None,
        db: Database,
        rabbitmq: RabbitMQClient,
    ) -> Container:
        return Container(
            settings=settings or get_settings(),
            db=db,
            rabbitmq=rabbitmq,
        )


def create_worker() -> Worker:
    settings = get_settings()

    database = Database.create(settings.db)
    rabbitmq = RabbitMQClient.create(settings.rabbitmq)

    container = Container.create(
        db=database,
        rabbitmq=rabbitmq,
    )

    consumers = [
        EmailVerificationConsumer(container),
    ]

    return Worker(
        consumers=consumers,
    )
