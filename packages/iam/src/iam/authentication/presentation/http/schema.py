from __future__ import annotations

from pydantic import BaseModel

from iam.authentication.application.dto import AuthenticationResult


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    user_id: str
    access_token: str

    @classmethod
    def from_result(cls, result: AuthenticationResult) -> LoginResponse:
        return cls(
            user_id=str(result.user_id),
            access_token=result.access_token,
        )
