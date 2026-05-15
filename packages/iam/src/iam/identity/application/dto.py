from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RegisterUserResult:
    user_id: UUID
    email: str

    verification_email_sent: bool


@dataclass(frozen=True, slots=True)
class EmailVerificationResult:
    user_id: UUID

    email_verified: bool


@dataclass(frozen=True, slots=True)
class ResendEmailVerificationCommand:
    user_id: UUID

    verification_email_sent: bool
