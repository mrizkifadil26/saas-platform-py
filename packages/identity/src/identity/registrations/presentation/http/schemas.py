from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, model_validator


class BeginEmailRegistrationRequest(BaseModel):
    email: EmailStr


class BeginEmailRegistrationResponse(BaseModel):
    # registration_id: str
    method: str
    step: str
    expires_at: datetime


class VerifyEmailRegistrationLinkRequest(BaseModel):
    token: str = Field(min_length=32)


class VerifyEmailRegistrationOtpRequest(BaseModel):
    code: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )


class VerifyEmailRegistrationResponse(BaseModel):
    # registration_id: str
    method: str
    step: str
    expires_at: datetime


class SetRegistrationPasswordRequest(BaseModel):
    password: str = Field(min_length=8, max_length=128)
    password_confirmation: str

    @model_validator(mode="after")
    def passwords_match(self) -> SetRegistrationPasswordRequest:
        if self.password != self.password_confirmation:
            raise ValueError("Passwords do not match")

        return self


class SetRegistrationPasswordResponse(BaseModel):
    # registration_id: str
    status: str


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None
