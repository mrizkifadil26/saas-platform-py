from dataclasses import dataclass

from iam.identity.domain.value_objects import EmailAddress, UserId


@dataclass(frozen=True, slots=True)
class AuthenticateUserCommand:
    email: EmailAddress
    password: str

    ip_address: str
    user_agent: str


@dataclass(frozen=True, slots=True)
class SetupPasswordCredentialCommand:
    user_id: UserId
    password: str
