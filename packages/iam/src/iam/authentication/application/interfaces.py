from datetime import timedelta
from typing import Any, Protocol

from iam.authentication.domain.value_objects import AccessToken, PasswordHash


class PasswordHasher(Protocol):
    def hash(
        self,
        plain_password: str,
    ) -> PasswordHash: ...


class CredentialVerifier(Protocol):
    def verify_password(
        self,
        *,
        password: str,
        password_hash: PasswordHash,
    ) -> bool: ...


class AccessTokenIssuer(Protocol):
    def issue(
        self,
        claims: dict[str, Any],
        expires_in: timedelta | None = None,
    ) -> AccessToken: ...
