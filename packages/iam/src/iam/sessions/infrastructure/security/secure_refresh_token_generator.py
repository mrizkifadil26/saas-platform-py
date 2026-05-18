import secrets

from iam.sessions.domain import RefreshTokenGenerator


class SecureRefreshTokenGenerator(RefreshTokenGenerator):
    def generate(self) -> str:
        return secrets.token_urlsafe(64)
