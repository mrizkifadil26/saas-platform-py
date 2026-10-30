import asyncio

from identity.shared.infrastructure.messaging.consumer import MessageConsumer
from identity.shared.infrastructure.messaging.rabbitmq.client import RabbitMQClient
from identity.shared.infrastructure.messaging.rabbitmq.consumer import RabbitMQTransportConsumer
from identity.shared.infrastructure.messaging.rabbitmq.settings import RabbitMQSettings
from identity.shared.infrastructure.messaging.registry import MessageHandlerRegistry
from identity.shared.infrastructure.messaging.serializers.json import JsonPayloadSerializer
from identity.workers.email_verification.handler import EmailSender, EmailVerificationHandler
from identity.workers.email_verification.worker import EmailVerificationWorker
from identity.workers.worker import StopSignal


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
