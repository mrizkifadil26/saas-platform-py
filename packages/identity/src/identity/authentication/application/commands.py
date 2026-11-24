from dataclasses import dataclass
from uuid import UUID

from identity.shared.application.command_bus.contracts import Command


@dataclass(frozen=True, slots=True)
class AuthenticateWithPassword(Command):
    email: str
    password: str

    ip_address: str | None
    user_agent: str | None


@dataclass(frozen=True, slots=True)
class Logout(Command):
    session_id: UUID


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
