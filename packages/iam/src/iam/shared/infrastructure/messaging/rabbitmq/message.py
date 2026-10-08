from aio_pika.abc import AbstractIncomingMessage

from iam.shared.application.messaging.transport import ReceivedMessage


class RabbitMQReceivedMessage(ReceivedMessage):
    def __init__(
        self,
        message: AbstractIncomingMessage,
    ) -> None:
        self._message = message

    @property
    def subject(self) -> str:
        assert self._message.routing_key is not None

        return self._message.routing_key

    @property
    def data(self) -> bytes:
        return self._message.body

    @property
    def attempt(self) -> int:
        return 0

    async def ack(self) -> None:
        await self._message.ack()

    async def retry(self, delay: float) -> None:
        raise NotImplementedError

    async def terminate(self) -> None:
        await self._message.reject(
            requeue=False,
        )
