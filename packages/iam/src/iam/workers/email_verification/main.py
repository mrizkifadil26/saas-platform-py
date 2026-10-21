import asyncio

from iam.shared.infrastructure.messaging.consumer import MessageConsumer
from iam.shared.infrastructure.messaging.rabbitmq.client import RabbitMQClient
from iam.shared.infrastructure.messaging.rabbitmq.consumer import RabbitMQTransportConsumer
from iam.shared.infrastructure.messaging.rabbitmq.settings import RabbitMQSettings
from iam.shared.infrastructure.messaging.registry import MessageHandlerRegistry
from iam.shared.infrastructure.messaging.serializers.json import JsonPayloadSerializer
from iam.workers.email_verification.handler import EmailSender, EmailVerificationHandler
from iam.workers.email_verification.worker import EmailVerificationWorker
from iam.workers.worker import StopSignal


async def main() -> None:
    stop = StopSignal()

    rabbitmq = await RabbitMQClient.create(
        RabbitMQSettings(),
        exchange_name="iam.events",
    )

    queue = await rabbitmq.declare_queue(
        "email-verification-worker",
        durable=True,
    )

    await rabbitmq.bind_queue(
        queue,
        routing_key="email.verification_requested",
    )

    serializer = JsonPayloadSerializer()

    transport = RabbitMQTransportConsumer(
        client=rabbitmq,
        queue=queue,
        serializer=serializer,
    )

    consumer = MessageConsumer(
        transport=transport,
    )

    sender = EmailSender()

    handler = EmailVerificationHandler(
        sender=sender,
    )

    registry = MessageHandlerRegistry()
    registry.register(
        "iam.email_verification.requested",
        handler,
    )

    worker = EmailVerificationWorker(
        consumer=consumer,
        registry=registry,
    )

    await worker.run(stop)


if __name__ == "__main__":
    asyncio.run(main())
