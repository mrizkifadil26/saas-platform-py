from dataclasses import dataclass

from identity.shared.infrastructure.email.template import EmailTemplate


@dataclass(frozen=True, slots=True)
class EmailVerificationTemplate(EmailTemplate):
    recipient: str
    verification_url: str
    expires_in: str

    name = "email_verification"

    def context(self) -> dict[str, object]:
        return {
            "verification_url": self.verification_url,
            "expires_in": self.expires_in,
        }
