from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from iam.identity.domain.value_objects import UserId
from iam.shared.domain import AggregateRoot

from .enums import SessionStatus
from .refresh_token import RefreshToken
from .value_objects import RefreshTokenHash, RefreshTokenId, SessionId


@dataclass(slots=True)
class Session(AggregateRoot[SessionId]):
    user_id: UserId

    status: SessionStatus

    created_at: datetime
    updated_at: datetime

    expires_at: datetime
    last_activity_at: datetime

    current_refresh_token_id: RefreshTokenId | None = None

    revoked_at: datetime | None = None

    ip_address: str | None = None
    user_agent: str | None = None
    device_name: str | None = None

    @classmethod
    def create(
        cls,
        *,
        user_id: UserId,
        created_at: datetime,
        ttl_days: int = 30,
        ip_address: str | None = None,
        user_agent: str | None = None,
        device_name: str | None = None,
    ) -> Session:
        session = cls(
            id=SessionId.generate(),
            user_id=user_id,
            status=SessionStatus.ACTIVE,
            created_at=created_at,
            updated_at=created_at,
            expires_at=created_at + timedelta(days=ttl_days),
            last_activity_at=created_at,
            ip_address=ip_address,
            user_agent=user_agent,
            device_name=device_name,
        )

        # TODO: emit sessioncreated event

        return session

    @property
    def is_revoked(self) -> bool:
        return self.status == SessionStatus.REVOKED

    def is_expired(
        self,
        now: datetime,
    ) -> bool:
        return now >= self.expires_at

    def is_active(
        self,
        now: datetime,
    ) -> bool:
        return self.status == SessionStatus.ACTIVE and not self.is_expired(now)

    def attach_refresh_token(
        self,
        refresh_token_id: RefreshTokenId,
        *,
        now: datetime,
    ) -> None:
        self.current_refresh_token_id = refresh_token_id
        self.last_activity_at = now
        self.updated_at = now

    def revoke(
        self,
        revoked_at: datetime,
    ) -> None:
        self.status = SessionStatus.REVOKED
        self.revoked_at = revoked_at
        self.updated_at = revoked_at

        # TODO: emit session revoked event

    def rotate_refresh_token(
        self,
        *,
        current_token: RefreshToken,
        new_token_hash: RefreshTokenHash,
        now: datetime,
        refresh_token_ttl: timedelta,
    ) -> RefreshToken:
        if self.is_revoked:
            # TODO: raise session revoked error
            raise

        if self.is_expired(now):
            # TODO: raise session expired error
            raise

        new_refresh_token = RefreshToken.create(
            session_id=self.id,
            token_hash=new_token_hash,
            created_at=now,
            expires_at=now + refresh_token_ttl,
            parent_token_id=current_token.id,
        )

        current_token.revoke(
            revoked_at=now,
            replaced_by=new_refresh_token.id,
        )

        current_token.mark_used(used_at=now)

        # TODO: do we really need touch updated_at and last_activity_at here?

        # TODO: emit refresh token rotated event
        return new_refresh_token
