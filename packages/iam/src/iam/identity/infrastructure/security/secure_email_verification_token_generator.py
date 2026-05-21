import secrets

from iam.identity.application import EmailVerificationTokenGenerator
from iam.identity.domain.value_objects import EmailVerificationToken


class SecureEmailVerificationTokenGenerator(
    EmailVerificationTokenGenerator,
):
    def __init__(
        self,
        *,
        token_bytes: int = 32,
    ) -> None:
        self._token_bytes = token_bytes

    def generate(
        self,
    ) -> EmailVerificationToken:
        return EmailVerificationToken(
            self._generate_raw_token(),
        )

    def _generate_raw_token(
        self,
    ) -> str:
        return secrets.token_urlsafe(
            self._token_bytes,
        )
