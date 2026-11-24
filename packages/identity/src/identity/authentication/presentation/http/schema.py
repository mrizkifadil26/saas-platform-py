from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, EmailStr, Field

from identity.authentication.application.dto import AuthenticationResult
from identity.sessions.application.dto import RefreshSessionResult


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class LoginResponse(TokenResponse):
    @classmethod
    def from_result(cls, result: AuthenticationResult) -> LoginResponse:
        return cls(
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            token_type="bearer",
            expires_in=result.expires_in,
        )


class RefreshSessionRequest(BaseModel):
    refresh_token: str


class RefreshSessionResponse(TokenResponse):
    @classmethod
    def from_result(
        cls,
        result: RefreshSessionResult,
    ) -> RefreshSessionResponse:
        return cls(
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            token_type="bearer",
            expires_in=result.expires_in,
        )


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=1, max_length=128)


class ChangePasswordResponse(BaseModel):
    message: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=128)


class ResetPasswordResponse(BaseModel):
    message: str
