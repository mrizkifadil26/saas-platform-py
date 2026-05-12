from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from iam.identity.domain.value_objects import UserId
from iam.sessions.domain.value_objects import SessionId
from iam.shared.domain import AggregateRoot


@dataclass(slots=True)
class Session(AggregateRoot[SessionId]):
    id: SessionId
    user_id: UserId
    token_hash: str
    expires_at: datetime
    created_at: datetime
    revoked: bool = False

    @classmethod
    def create(
        cls,
        user_id: UserId,
        token_hash: str,
        ttl: timedelta,
        *,
        created_at: datetime,
    ) -> Session:
        return cls(
            id=SessionId.generate(),
            user_id=user_id,
            token_hash=token_hash,
            created_at=created_at,
            expires_at=created_at + ttl,
        )

    def revoke(self) -> None:
        self.revoked = True

    def is_expired(
        self,
        *,
        now: datetime,
    ) -> bool:
        return now >= self.expires_at

    def is_active(
        self,
        *,
        now: datetime,
    ) -> bool:
        return not self.revoked and not self.is_expired(now=now)
