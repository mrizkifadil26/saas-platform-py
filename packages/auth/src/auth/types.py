from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, TypedDict


class AccessTokenClaims(TypedDict):
    iss: str
    aud: str
    sub: str  # user_id as str
    exp: int  # epoch seconds
    iat: int  # epoch seconds
    jti: str  # unique token id

    # app-specific
    sid: str  # session_id
    wid: str  # workspace_id
    typ: Literal["access"]


@dataclass(frozen=True, slots=True)
class TokenPair:
    access_token: str
    refresh_token: str
    access_expires_at: datetime


@dataclass(frozen=True, slots=True)
class AuthenticatedSubject:
    user_id: uuid.UUID
    workspace_id: uuid.UUID
    session_id: uuid.UUID
