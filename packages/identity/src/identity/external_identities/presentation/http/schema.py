from __future__ import annotations

from datetime import datetime
from typing import Literal

from identity.registration.application.dto import EmailVerificationResult
from pydantic import BaseModel, EmailStr, Field


class RegistrationRequest(BaseModel):
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
    # registration_id: UUID
    token: str = Field(min_length=6, max_length=6)


class EmailVerificationResponse(BaseModel):
    # registration_id: UUID
    message: str
    status: Literal[
        "pending_email_verification",
        "completed",
        "expired",
    ]

    @classmethod
    def from_result(cls, result: EmailVerificationResult) -> EmailVerificationResponse:
        return EmailVerificationResponse(
            message="",
            status="completed",
        )


class EmailVerificationResendRequest(BaseModel):
    # registration_id: UUID
    email: EmailStr


class EmailVerificationResendResponse(BaseModel):
    # registration_id: UUID
    message: str
