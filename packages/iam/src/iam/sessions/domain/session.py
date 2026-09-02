from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from iam.identity.domain.value_objects import UserId
from iam.shared.domain import AggregateRoot

from .enums import SessionStatus
from .value_objects import RefreshTokenId, SessionId


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
        expires_at: datetime,
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
            expires_at=expires_at,
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
        # self._ensure_active(now=now)

        self.current_refresh_token_id = refresh_token_id
        self.last_activity_at = now
        self.updated_at = now

    def rotate_to(
        self,
        *,
        # current_token: RefreshToken,
        # new_token_hash: RefreshTokenHash,
        current_token_id: RefreshTokenId,
        new_token_id: RefreshTokenId,
        now: datetime,
        # refresh_token_ttl: timedelta,
        # ) -> RefreshToken:
    ) -> None:
        # self._ensure_active(now=now)
        #
        # if self.current_refresh_token_id != current_token_id:
        #   raise

        # if self.is_revoked:
        # TODO: raise session revoked error
        # raise

        # if self.is_expired(now):
        # TODO: raise session expired error
        # raise

        # new_refresh_token = RefreshToken.create(
        #     session_id=self.id,
        #     token_hash=new_token_hash,
        #     created_at=now,
        #     expires_at=now + refresh_token_ttl,
        #     parent_token_id=current_token.id,
        # )

        # current_token.revoke(
        #     revoked_at=now,
        #     replaced_by=new_refresh_token.id,
        # )

        # current_token.mark_used(used_at=now)

        # self.attach_refresh_token(
        #     new_refresh_token.id,
        #     now=now,
        # )

        self.current_refresh_token_id = new_token_id
        self.last_activity_at = now
        self.updated_at = now

        # TODO: emit refresh token rotated event
        # return new_refresh_token

    def revoke(
        self,
        revoked_at: datetime,
    ) -> None:
        if self.is_revoked:
            return

        self.status = SessionStatus.REVOKED
        self.revoked_at = revoked_at
        self.updated_at = revoked_at

        # TODO: emit session revoked event

    def _ensure_active(
        self,
        *,
        now: datetime,
    ) -> None:
        if self.is_revoked:
            # raise SessionRevokedError()
            raise

        if self.is_expired(now=now):
            # raise SessionExpiredError()
            raise
