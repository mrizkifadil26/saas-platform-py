from datetime import datetime
from typing import Protocol

from iam.authentication.domain.value_objects import (
    AccessToken,
    RefreshToken,
    RegistrationToken,
)
from iam.authentication.infrastructure.security.jwt_payloads import (
    RegistrationTokenPayload,
)
from iam.identity.domain.value_objects import UserId

# from iam.organizations.domain.value_objects.organization_id import OrganizationId
# from .dto import AuthTokens


class PasswordHasher(Protocol):
    async def hash(self, plain_password: str) -> str: ...

    async def verify(
        self,
        plain_password: str,
        password_hash: str,
    ) -> bool: ...


class TokenProvider(Protocol):
    async def generate_access_token(
        self,
        user_id: UserId,
        # organization_id: OrganizationId | None = None,
        permissions: frozenset[str] = frozenset(),
    ) -> AccessToken: ...

    async def generate_refresh_token(
        self,
        user_id: UserId,
        # organization_id: OrganizationId | None = None,
        permissions: frozenset[str] = frozenset(),
    ) -> RefreshToken: ...

    async def verify_access_token(
        self,
        token: AccessToken,
    ) -> object: ...

    async def verify_refresh_token(
        self,
        token: RefreshToken,
    ) -> object: ...


class RegistrationTokenProvider(Protocol):
    async def generate_token(
        self,
        user_id: UserId,
        *,
        issued_at: datetime,
    ) -> RegistrationToken: ...

    async def verify_token(
        self,
        token: RegistrationToken,
    ) -> RegistrationTokenPayload: ...
