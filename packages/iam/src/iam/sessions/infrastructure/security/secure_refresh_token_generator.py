import secrets

from iam.sessions.application import RefreshTokenGenerator
from iam.sessions.domain.value_objects import RefreshTokenSecret


class SecureRefreshTokenGenerator(RefreshTokenGenerator):
    def __init__(
        self,
        *,
        token_bytes: int = 64,
    ) -> None:
        self._token_bytes = token_bytes

    def generate(self) -> RefreshTokenSecret:
        return RefreshTokenSecret(
            self._generate_raw_token(),
        )

    def _generate_raw_token(
        self,
    ) -> str:
        return secrets.token_urlsafe(
            self._token_bytes,
        )
