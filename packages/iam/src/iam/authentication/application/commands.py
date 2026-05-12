from dataclasses import dataclass

from iam.authentication.domain.value_objects import RefreshToken, RegistrationToken
from iam.identity.domain.value_objects import EmailAddress


@dataclass(frozen=True, slots=True)
class RequestRegistrationCommand:
    email: EmailAddress


@dataclass(frozen=True, slots=True)
class VerifyEmailCommand:
    token: RegistrationToken


@dataclass(frozen=True, slots=True)
class SetupPasswordCommand:
    token: RegistrationToken
    password: str


@dataclass(frozen=True, slots=True)
class ConfirmRegistrationCommand:
    token: str
    full_name: str
    plain_password: str


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
