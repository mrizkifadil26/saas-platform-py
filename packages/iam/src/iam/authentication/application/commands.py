from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AuthenticateUserCommand:
    email: str
    password: str

    ip_address: str
    user_agent: str


@dataclass(frozen=True, slots=True)
class SetupPasswordCredentialCommand:
    user_id: UUID
    password: str
