from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr


class BeginEmailRegistrationRequest(BaseModel):
    email: EmailStr
    resume_token: str | None = None


class BeginEmailRegistrationResponse(BaseModel):
    registration_id: str
    method: str
    step: str
    expires_at: datetime


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None
