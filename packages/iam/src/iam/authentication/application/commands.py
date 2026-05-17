from dataclasses import dataclass
from uuid import UUID

from iam.authentication.domain.value_objects import RefreshToken


@dataclass(frozen=True, slots=True)
class AuthenticateUserCommand:
    email: str
    password: str

    ip_address: str
    user_agent: str


@dataclass(frozen=True, slots=True)
class RefreshAuthenticationCommand:
    refresh_token: RefreshToken

    ip_address: str
    user_agent: str


@dataclass(frozen=True, slots=True)
class SetupPasswordCredentialCommand:
    user_id: UUID
    password: str
