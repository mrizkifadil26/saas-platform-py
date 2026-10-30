from asyncio import Protocol
from email.message import EmailMessage


class EmailSender(Protocol):
    async def send(
        self,
        email: EmailMessage,
    ) -> None: ...
