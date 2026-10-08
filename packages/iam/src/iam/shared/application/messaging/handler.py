from typing import Protocol, TypeVar

from .message import MessageEnvelope

T = TypeVar("T")


class MessageHandler(Protocol[T]):
    async def __call__(
        self,
        message: MessageEnvelope[T],
    ) -> None: ...
