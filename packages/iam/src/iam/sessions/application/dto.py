from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from iam.sessions.domain.value_objects import SessionId


@dataclass(frozen=True, slots=True)
class SessionResult:
    session_id: SessionId
    tokens: SessionTokens
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class SessionTokens:
    access_token: str
    refresh_token: str
