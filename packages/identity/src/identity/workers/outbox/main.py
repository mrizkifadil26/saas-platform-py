import asyncio
import logging
import signal

from identity.shared.infrastructure.messaging.rabbitmq.client import RabbitMQClient
from identity.shared.infrastructure.messaging.rabbitmq.settings import RabbitMQSettings
from identity.shared.infrastructure.outbox.publisher import (
    DefaultMessagePublisher,
    OutboxPublisher,
)
from identity.shared.infrastructure.outbox.relay import OutboxRelay
from identity.shared.infrastructure.outbox.retry import RetryPolicy
from identity.shared.infrastructure.outbox.sqlalchemy.sqlalchemy_outbox_repository import (
    SQLAlchemyOutboxRepository,
)
from identity.shared.infrastructure.time.system_clock import SystemClock
from identity.workers.outbox.worker import OutboxWorker
from identity.workers.worker import StopSignal

from db import AppDBSettings, Database

logger = logging.getLogger(__name__)


async def main() -> None:
    stop = StopSignal()
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.stop)

    database = Database.create(
        AppDBSettings(url=""),
    )
    rabbitmq = await RabbitMQClient.create(
        RabbitMQSettings(),
    )

    message_publisher = DefaultMessagePublisher(rabbitmq)

    try:
        clock = SystemClock()

        outbox_repository = SQLAlchemyOutboxRepository(
            session_factory=database.session_factory,
        )

        publisher = OutboxPublisher(
            repository=outbox_repository,
            publisher=message_publisher,
            retry_policy=RetryPolicy(),
            clock=clock,
        )

        relay = OutboxRelay(
            publisher=publisher,
            clock=clock,
        )

        worker = OutboxWorker(relay)

        await worker.run(stop)
    finally:
        await rabbitmq.close()
        await database.stop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.remove_signal_handler(sig)


if __name__ == "__main__":
    asyncio.run(main())
