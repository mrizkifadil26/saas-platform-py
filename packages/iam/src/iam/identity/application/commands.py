from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RegisterUserCommand:
    email: str


@dataclass(frozen=True, slots=True)
class VerifyEmailCommand:
    token: str


@dataclass(frozen=True, slots=True)
class ResendEmailVerificationCommand:
    user_id: UUID
