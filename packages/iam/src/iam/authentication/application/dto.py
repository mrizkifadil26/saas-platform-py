from dataclasses import dataclass

from iam.authentication.domain.value_objects import (
    AuthenticationTokens,
    RegistrationToken,
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
class RegistrationResult:
    user_id: UserId
    verification_token: RegistrationToken


@dataclass(frozen=True, slots=True)
class VerifyEmailResult:
    user_id: UserId
    password_setup_required: bool = True


@dataclass(frozen=True, slots=True)
class SetupPasswordResult:
    user_id: UserId
