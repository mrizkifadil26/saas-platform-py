from typing import Any

from iam.shared.application.email_sender import EmailSender


class SendVerificationEmailHandler:
    def __init__(
        self,
        email_sender: EmailSender,
    ) -> None:
        self._email_sender = email_sender

    async def handle(self, message: Any) -> None:
        await self._email_sender.send(
            to=message["email"],
            template="email_verification",
            variables={
                "verification_token": message["verification_token"],
            },
        )
