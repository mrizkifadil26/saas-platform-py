from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from iam.shared.domain import AggregateRoot

from .value_objects import EmailVerificationId, EmailVerificationTokenHash, UserId


@dataclass(slots=True)
class EmailVerification(AggregateRoot[EmailVerificationId]):
    user_id: UserId

    token_hash: EmailVerificationTokenHash

    expires_at: datetime
    created_at: datetime

    verified_at: datetime | None = None

    @classmethod
    def create(
        cls,
        *,
        user_id: UserId,
        token_hash: EmailVerificationTokenHash,
        created_at: datetime,
        ttl_minutes: int = 15,
    ) -> EmailVerification:
        verification = cls(
            id=EmailVerificationId.generate(),
            user_id=user_id,
            token_hash=token_hash,
            expires_at=created_at + timedelta(minutes=ttl_minutes),
            created_at=created_at,
        )

        # TODO: record email verification created

        return verification

    @property
    def is_verified(self) -> bool:
        return self.verified_at is not None

    def is_expired(
        self,
        *,
        now: datetime,
    ) -> bool:
        return now >= self.expires_at

    def verify(
        self,
        token_hash: EmailVerificationTokenHash,
        *,
        verified_at: datetime,
    ) -> None:
        if self.is_verified:
            # TODO: raise already consuumed error
            raise

        if self.is_expired(now=verified_at):
            # TODO: raise email verification expired error
            raise

        if self.token_hash != token_hash:
            # TODO: raise invalid email verification error
            raise

        # TODO: record email verification consumed9
        self.consumed_at = verified_at
