import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from db import create_engine, create_session_factory
from iam.shared.application.messaging.outbox import OutboxRepository
from iam.shared.application.messaging.outbox.publisher import OutboxPublisher
from iam.shared.application.messaging.publisher import (
    DefaultMessagePublisher,
    MessagePublisher,
)
from iam.shared.infrastructure.messaging.json_message_serializer import (
    JSONMessageSerializer,
)
from iam.shared.infrastructure.messaging.outbox.sqlalchemy.sqlalchemy_outbox_repository import (
    SQLAlchemyOutboxRepository,
)
from iam.shared.infrastructure.messaging.rabbitmq.transport import (
    RabbitMQConnection,
    RabbitMQTransport,
)
from iam.workers.outbox.worker import OutboxWorker
from iam.workers.worker import StopSignal


@dataclass(frozen=True)
class MessagingContext:
    outbox: OutboxRepository
    publisher: MessagePublisher


@asynccontextmanager
async def create_messaging_context() -> AsyncIterator[MessagingContext]:
    engine = create_engine(...)
    session_factory = create_session_factory(engine)

    rabbitmq_conn = RabbitMQConnection(...)
    await rabbitmq_conn.connect()

    rabbitmq = RabbitMQTransport(connection=rabbitmq_conn)
    outbox = SQLAlchemyOutboxRepository(session=session_factory)
    publisher = DefaultMessagePublisher(
        serializer=JSONMessageSerializer(),
        transport=rabbitmq,
    )

    try:
        yield MessagingContext(outbox=outbox, publisher=publisher)
    finally:
        await rabbitmq_conn.close()
        await engine.dispose()


async def main() -> None:
    stop = StopSignal()

    async with create_messaging_context() as ctx:
        await OutboxWorker(
            publisher=OutboxPublisher(ctx.outbox, ctx.publisher),
        ).run(stop)


if __name__ == "__main__":
    asyncio.run(main())
