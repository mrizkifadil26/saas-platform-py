from datetime import datetime
import uuid
from typing import Protocol


class UserRecord(Protocol):
    id: uuid.UUID
    email: str
    password_hash: str
    is_active: bool


class SessionRecord(Protocol):
    id: uuid.UUID
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    token_hash: bytes
    expires_at: datetime
    revoked_at: datetime | None
