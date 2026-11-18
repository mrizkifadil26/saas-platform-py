from typing import Protocol

from .message import Message


class MessageHandler(Protocol):
    async def __call__(
        self,
        message: Message,
    ) -> None: ...
