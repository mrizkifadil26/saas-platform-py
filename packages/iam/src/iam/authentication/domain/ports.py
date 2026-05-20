from datetime import timedelta
from typing import Any, Protocol

from iam.authentication.domain import Credential

from .value_objects import AccessToken, PasswordHash


class PasswordHasher(Protocol):
    def hash(
        self,
        plain_password: str,
    ) -> PasswordHash: ...


class CredentialVerifier(Protocol):
    def verify_password(
        self,
        *,
        credential: Credential,
        password: str,
    ) -> bool: ...


class AccessTokenIssuer(Protocol):
    def issue(
        self,
        claims: dict[str, Any],
        expires_in: timedelta | None = None,
    ) -> AccessToken: ...
