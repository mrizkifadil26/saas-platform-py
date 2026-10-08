from iam.identity.application.dto import SendEmailVerificationRequest
from iam.shared.application.email_sender import EmailSender
from iam.shared.application.messaging.message import MessageEnvelope


class SendVerificationEmailHandler:
    def __init__(
        self,
        email_sender: EmailSender,
    ) -> None:
        self._email_sender = email_sender

    async def __call__(
        self,
        message: MessageEnvelope[SendEmailVerificationRequest],
    ) -> None:
        event = message.payload

        await self._email_sender.send(
            to=event.email,
            subject="Verify your email",
            template=(
                "Click the link below to verify your email:\n\n"
                f"https://example.com/verify-email"
                f"?token={event.verification_token}"
            ),
            variables={},
        )
