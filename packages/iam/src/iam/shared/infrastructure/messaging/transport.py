from collections.abc import AsyncIterator
from typing import Protocol

from iam.shared.infrastructure.messaging.message import ReceivedMessage

# @dataclass(frozen=True, slots=True)
# class OutgoingMessage:
#     subject: str
#     data: bytes
#     message_id: str
#     headers: dict[str, str] = field(default_factory=lambda: dict[str, str]())


# class ReceivedMessage(Protocol):
#     @property
#     def subject(self) -> str: ...

#     @property
#     def data(self) -> bytes: ...

#     @property
#     def attempt(self) -> int: ...

#     async def ack(self) -> None: ...

#     async def retry(self, delay: float) -> None: ...

#     async def terminate(self) -> None: ...


class TransportPublisher(Protocol):
    # async def publish(
    #     self,
    #     message: OutgoingMessage,
    # ) -> None: ...
    async def publish(
        self,
        *,
        message_id: str,
        message_type: str,
        payload: bytes,
    ) -> None: ...


class TransportConsumer(Protocol):
    # def consume(
    #     self,
    #     *,
    #     subject: str,
    #     consumer_name: str,
    # ) -> AsyncIterator[ReceivedMessage]: ...
    def consume(self) -> AsyncIterator[ReceivedMessage]: ...
