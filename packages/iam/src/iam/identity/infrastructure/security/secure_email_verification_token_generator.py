import secrets

from iam.identity.domain.value_objects import EmailVerificationToken


class SecureEmailVerificationTokenGenerator:
    def __init__(
        self,
        *,
        token_bytes: int = 32,
    ) -> None:
        self._token_bytes = token_bytes

    def generate(
        self,
    ) -> EmailVerificationToken:
        token_value = secrets.token_urlsafe(
            self._token_bytes,
        )

        return EmailVerificationToken(token_value)
