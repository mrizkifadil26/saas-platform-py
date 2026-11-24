from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from identity.sessions.application.dto import RefreshSessionResult


class RefreshSessionRequest(BaseModel):
    refresh_token: str


class RefreshSessionResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int

    @classmethod
    def from_result(
        cls,
        result: RefreshSessionResult,
    ) -> RefreshSessionResponse:
        return cls(
            access_token=result.access_token.value,
            expires_in=result.access_token_expires_in,
        )
