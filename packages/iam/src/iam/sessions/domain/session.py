from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from iam.identity.domain.value_objects import UserId
from iam.shared.domain import AggregateRoot

from .enums import SessionStatus
from .refresh_token import RefreshToken
from .value_objects import RefreshTokenHash, SessionId


@dataclass(slots=True)
class Session(AggregateRoot[SessionId]):
    user_id: UserId
    refresh_tokens: list[RefreshToken]
    # TODO: later track session device

    created_at: datetime
    updated_at: datetime

    expires_at: datetime
    last_activity_at: datetime

    status: SessionStatus = SessionStatus.ACTIVE

    revoked_at: datetime | None = None

    @classmethod
    def create(
        cls,
        *,
        user_id: UserId,
        refresh_token: RefreshToken,
        created_at: datetime,
        ttl_days: int = 30,
    ) -> Session:
        session = cls(
            id=SessionId.generate(),
            user_id=user_id,
            refresh_tokens=[refresh_token],
            created_at=created_at,
            updated_at=created_at,
            expires_at=created_at + timedelta(days=ttl_days),
            last_activity_at=created_at,
        )

        # TODO: emit sessioncreated event

        return session

    @property
    def active_refresh_token(self) -> RefreshToken:
        return self.refresh_tokens[-1]

    @property
    def is_revoked(self) -> bool:
        return self.status == SessionStatus.REVOKED

    def revoke(
        self,
        revoked_at: datetime,
    ) -> None:
        self.status = SessionStatus.REVOKED
        self.revoked_at = revoked_at
        self.updated_at = revoked_at

        # TODO: emit session revoked event

    def is_expired(
        self,
        *,
        now: datetime,
    ) -> bool:
        return now >= self.expires_at

    def touch(self, *, now: datetime) -> None:
        self.last_activity_at = now
        self.updated_at = now

    def rotate_refresh_token(
        self,
        *,
        current_token_hash: RefreshTokenHash,
        new_refresh_token: RefreshToken,
        rotated_at: datetime,
    ) -> None:
        if self.is_revoked:
            # TODO: raise session revoked error
            raise

        if self.is_expired(now=rotated_at):
            # TODO: raise session expired error
            raise

        current_token = next(
            (
                token
                for token in self.refresh_tokens
                if token.token_hash == current_token_hash
            ),
            None,
        )

        if current_token is None:
            # TODO: raise invalid refresh token error
            raise

        if current_token.is_revoked:
            self.revoke(rotated_at)

            # TODO: emit refresh token reuse detected event
            # TODO: raise refresh reuse error

        current_token.revoke(
            revoked_at=rotated_at,
            replaced_by=new_refresh_token.token_hash,
        )

        self.refresh_tokens.append(new_refresh_token)

        self.last_activity_at = rotated_at
        self.updated_at = rotated_at

        # TODO: emit refresh token rotated event
