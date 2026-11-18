from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AuthenticationResult:
    user_id: UUID
    session_id: UUID

    access_token: str
    refresh_token: str

    expires_at: datetime


@dataclass(frozen=True, slots=True)
class SetupPasswordResult:
    user_id: UUID
