from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .value_objects import RefreshTokenHash


@dataclass(slots=True)
class RefreshToken:
    token_hash: RefreshTokenHash

    expires_at: datetime
    created_at: datetime
    revoked_at: datetime | None = None

    replaced_by_token_hash: RefreshTokenHash | None = None

    @classmethod
    def create(
        cls,
        token_hash: RefreshTokenHash,
        *,
        created_at: datetime,
        expires_at: datetime,
    ) -> RefreshToken:
        return cls(
            token_hash=token_hash,
            created_at=created_at,
            expires_at=expires_at,
        )

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    def is_expired(self, *, now: datetime) -> bool:
        return now >= self.expires_at

    def revoke(
        self,
        revoked_at: datetime,
        replaced_by: RefreshTokenHash | None = None,
    ) -> None:
        self.revoked_at = revoked_at
        self.replaced_by_token_hash = replaced_by

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RefreshToken):
            return False

        return self.token_hash == other.token_hash

    def __hash__(self) -> int:
        return hash(self.token_hash)
