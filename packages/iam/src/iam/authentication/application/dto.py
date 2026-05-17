from dataclasses import dataclass
from uuid import UUID

from iam.authentication.domain.value_objects import (
    AuthenticationTokens,
)
from iam.identity.domain.value_objects import UserId


@dataclass(frozen=True, slots=True)
class AuthTokens:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    user_id: UserId
    # session_id: SessionId


@dataclass(frozen=True, slots=True)
class AuthenticationResult:
    authenticated_user: AuthenticatedUser
    tokens: AuthenticationTokens


@dataclass(frozen=True, slots=True)
class SetupPasswordResult:
    user_id: UUID
