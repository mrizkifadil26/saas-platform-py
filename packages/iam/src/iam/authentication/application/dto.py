from dataclasses import dataclass
from uuid import UUID

from iam.authentication.domain.value_objects import AccessToken
from iam.identity.domain.value_objects import UserId
from iam.sessions.domain.value_objects import SessionId


@dataclass(frozen=True, slots=True)
class AuthenticationResult:
    user_id: UserId
    session_id: SessionId
    access_token: str
    refresh_token: str


@dataclass(frozen=True, slots=True)
class SetupPasswordResult:
    user_id: UUID


@dataclass(frozen=True, slots=True)
class IssuedAccessToken:
    token: AccessToken
    # payload: AccessTokenPayload
