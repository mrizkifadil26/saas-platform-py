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


@dataclass(frozen=True, slots=True)
class ChangePasswordCommand:
    user_id: UUID
    current_password: str
    new_password: str


@dataclass(frozen=True, slots=True)
class ForgotPasswordCommand:
    email: str


@dataclass(frozen=True, slots=True)
class ResetPasswordCommand:
    token: str
    new_password: str
