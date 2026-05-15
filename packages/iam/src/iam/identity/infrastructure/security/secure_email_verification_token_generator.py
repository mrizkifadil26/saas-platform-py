import secrets

from iam.identity.domain import EmailVerificationTokenGenerator
from iam.identity.domain.value_objects import EmailVerificationToken


class SecureEmailVerificationTokenGenerator(EmailVerificationTokenGenerator):
    def __init__(
        self,
        *,
        length: int = 32,
    ):
        self._length = length

    def generate(self) -> EmailVerificationToken:
        return EmailVerificationToken(self._generate_token())

    def _generate_token(self) -> str:
        return secrets.token_urlsafe(
            self._length,
        )
