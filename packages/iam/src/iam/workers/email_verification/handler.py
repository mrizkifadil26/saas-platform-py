from iam.identity.application.dto import SendEmailVerificationRequest
from iam.shared.application.messaging.message import MessageEnvelope
from iam.shared.infrastructure.email.templates import TemplateRenderer


class EmailVerificationHandler:
    def __init__(
        self,
        mailer: Mailer,
    ) -> None:
        self._mailer = mailer

    async def __call__(
        self,
        message: MessageEnvelope[SendEmailVerificationRequest],
    ) -> None:
        event = message.payload

        url = build_verification_url(
            event.verification_token,
        )

        email = render_verification_email(
            self._renderer,
            recipient=event.email,
            verification_url=url,
            expires_at=event.expires_at,
        )

        await self._mailer.send(email)
        # to=event.email,
        # subject="Verify your email",
        # template=(
        #     "Click the link below to verify your email:\n\n"
        #     f"https://example.com/verify-email"
        #     f"?token={event.verification_token}"
        # ),
        # variables={},
        # )


def render_verification_email(
    renderer: TemplateRenderer,
    *,
    recipient: str,
    verification_url: str,
    expires_at: datetime,
) -> Email: ...


@dataclass(frozen=True, slots=True)
class MailContext:
    mailer: Mailer
    renderer: TemplateRenderer
