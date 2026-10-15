import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from iam.shared.application.messaging.consumer import MessageConsumer
from iam.shared.infrastructure.email.console import ConsoleEmailSender
from iam.shared.infrastructure.messaging.json_message_serializer import (
    JSONMessageSerializer,
)
from iam.shared.infrastructure.messaging.rabbitmq.connection import RabbitMQConnection
from iam.shared.infrastructure.messaging.rabbitmq.transport import RabbitMQTransport
from iam.workers.email_verification.handler import SendVerificationEmailHandler
from iam.workers.email_verification.worker import EmailVerificationWorker
from iam.workers.worker import StopSignal


@dataclass(frozen=True)
class MessagingContext:
    rabbitmq_connection: RabbitMQConnection


@asynccontextmanager
async def create_messaging_context() -> AsyncIterator[MessagingContext]:
    rabbitmq = RabbitMQConnection(...)
    await rabbitmq.connect()

    try:
        yield MessagingContext(rabbitmq_connection=rabbitmq)
    finally:
        await rabbitmq.close()


async def main() -> None:
    stop = StopSignal()

    async with create_messaging_context() as ctx:
        await EmailVerificationWorker(
            consumer=MessageConsumer(
                transport=RabbitMQTransport(ctx.rabbitmq_connection),
                serializer=JSONMessageSerializer(),
                handler=SendVerificationEmailHandler(
                    email_sender=ConsoleEmailSender(),
                ),
            )
        ).run(stop)


if __name__ == "__main__":
    asyncio.run(main())
