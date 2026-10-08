from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegistrationCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    name: str = Field(min_length=1, max_length=100)


class RegistrationResponse(BaseModel):
    registration_id: str  # TODO: should be UUID i think
    email: EmailStr
    status: Literal[
        "pending_email_verification",
        "completed",
        "expired",
    ]
    expires_at: datetime | None


class EmailVerificationRequest(BaseModel):
    registration_id: UUID
    code: str = Field(min_length=6, max_length=6)


class EmailVerificationResendRequest(BaseModel):
    registration_id: UUID
