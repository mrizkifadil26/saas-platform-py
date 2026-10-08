from dataclasses import dataclass, field
from typing import AsyncIterator, Protocol


@dataclass(frozen=True, slots=True)
class OutgoingMessage:
    subject: str
    data: bytes
    message_id: str
    headers: dict[str, str] = field(default_factory=lambda: dict[str, str]())


class ReceivedMessage(Protocol):
    @property
    def subject(self) -> str: ...

    @property
    def data(self) -> bytes: ...

    @property
    def attempt(self) -> int: ...

    async def ack(self) -> None: ...

    async def retry(self, delay: float) -> None: ...

    async def terminate(self) -> None: ...


class TransportPublisher(Protocol):
    async def publish(
        self,
        message: OutgoingMessage,
    ) -> None: ...


class TransportConsumer(Protocol):
    def consume(
        self,
        *,
        subject: str,
        consumer_name: str,
    ) -> AsyncIterator[ReceivedMessage]: ...
