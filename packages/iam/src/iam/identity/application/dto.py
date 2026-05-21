from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UserDTO:
    id: UUID
    email: str
    is_verified: bool
    created_at: datetime


@dataclass(frozen=True, slots=True)
class RegisterUserResult:
    user: UserDTO
    email_verification_required: bool
    verification_expires_at: datetime | None


@dataclass(frozen=True, slots=True)
class EmailVerificationResult:
    user: UserDTO

    email_verified: bool


@dataclass(frozen=True, slots=True)
class ResendEmailVerificationCommand:
    user_id: UUID

    verification_email_sent: bool
