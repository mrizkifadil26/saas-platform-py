from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from identity.identity.domain.value_objects import UserId
from identity.sessions.domain.value_objects import (
    AccessToken,
    RefreshToken,
    RefreshTokenSecret,
    SessionId,
)


@dataclass(frozen=True, slots=True)
class SessionDTO:
    id: SessionId
    user_id: UserId
    created_at: datetime
    expires_at: datetime

    last_seen_at: datetime | None
    revoked_at: datetime | None

    user_agent: str | None
    ip_address: str | None


@dataclass(frozen=True, slots=True)
class SessionResult:
    session_id: SessionId
    tokens: SessionTokens
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class SessionTokens:
    access_token: str
    refresh_token: str


@dataclass(frozen=True, slots=True)
class IssuedSession:
    session_id: SessionId
    access_token: AccessToken
    refresh_token: RefreshTokenSecret


@dataclass(frozen=True, slots=True)
class RotatedSessionTokens:
    access_token: AccessToken
    refresh_token: RefreshTokenSecret


@dataclass(frozen=True, slots=True)
class RefreshSessionResult:
    access_token: AccessToken
    access_token_expires_in: int

    refresh_token: RefreshToken
    refresh_token_max_age: int | None
