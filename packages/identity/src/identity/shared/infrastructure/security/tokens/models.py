from dataclasses import dataclass
from datetime import datetime
from typing import Mapping


@dataclass(frozen=True, slots=True)
class TokenClaims:
    subject: str
    token_id: str
    issued_at: datetime
    expires_at: datetime
    claims: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class AccessToken:
    value: str
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class RefreshToken:
    value: str
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class TokenPair:
    access: AccessToken
    refresh: RefreshToken
