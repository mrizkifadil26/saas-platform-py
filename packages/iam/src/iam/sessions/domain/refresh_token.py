from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from iam.shared.domain import AggregateRoot

from .value_objects import RefreshTokenHash, RefreshTokenId, SessionId


@dataclass(slots=True)
class RefreshToken(AggregateRoot[RefreshTokenId]):
    session_id: SessionId
    token_hash: RefreshTokenHash

    created_at: datetime
    expires_at: datetime

    revoked_at: datetime | None = None
    used_at: datetime | None = None
    # revoked_reason: str | None = None

    replaced_by_token_id: RefreshTokenId | None = None
    parent_token_id: RefreshTokenId | None = None

    @classmethod
    def create(
        cls,
        *,
        session_id: SessionId,
        token_hash: RefreshTokenHash,
        created_at: datetime,
        expires_at: datetime,
        parent_token_id: RefreshTokenId | None = None,
    ) -> RefreshToken:
        return cls(
            id=RefreshTokenId.generate(),
            session_id=session_id,
            token_hash=token_hash,
            created_at=created_at,
            expires_at=expires_at,
            parent_token_id=parent_token_id,
        )

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

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
        return (
            not self.is_expired(now=now)
            and not self.is_revoked  # force split
            and not self.is_used
        )

    def replace_with(
        self,
        refresh_token_id: RefreshTokenId,
        *,
        used_at: datetime,
    ) -> None:
        if self.is_used:
            # raise RefreshTokenReuseDetectedError()
            raise

        if self.is_revoked:
            # raise RefreshTokenRevokedError()
            raise

        if self.is_expired(now=used_at):
            # raise RefreshTokenExpiredError()
            raise

        self.used_at = used_at
        self.revoked_at = used_at
        self.replaced_by_token_id = refresh_token_id

    def revoke(
        self,
        *,
        revoked_at: datetime,
    ) -> None:
        if self.is_revoked:
            return

        self.revoked_at = revoked_at
        # self.revoked_reason = reason

    def mark_used(
        self,
        *,
        used_at: datetime,
    ) -> None:
        self.used_at = used_at
