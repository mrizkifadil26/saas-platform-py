from dataclasses import dataclass

from iam.authentication.domain.value_objects import RefreshToken
from iam.identity.domain.value_objects import EmailAddress


@dataclass(frozen=True, slots=True)
class AuthenticateUserCommand:
    email: EmailAddress
    password: str

    ip_address: str
    user_agent: str


@dataclass(frozen=True, slots=True)
class RefreshAuthenticationCommand:
    refresh_token: RefreshToken

    ip_address: str
    user_agent: str
