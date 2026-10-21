import asyncio
import logging
import signal

from db import AppDBSettings, Database
from iam.shared.infrastructure.messaging.rabbitmq.client import RabbitMQClient
from iam.shared.infrastructure.messaging.rabbitmq.settings import RabbitMQSettings
from iam.shared.infrastructure.outbox.publisher import (
    DefaultMessagePublisher,
    OutboxPublisher,
)
from iam.shared.infrastructure.outbox.relay import OutboxRelay
from iam.shared.infrastructure.outbox.retry import RetryPolicy
from iam.shared.infrastructure.outbox.sqlalchemy.sqlalchemy_outbox_repository import (
    SQLAlchemyOutboxRepository,
)
from iam.shared.infrastructure.time.system_clock import SystemClock
from iam.workers.outbox.worker import OutboxWorker
from iam.workers.worker import StopSignal

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
