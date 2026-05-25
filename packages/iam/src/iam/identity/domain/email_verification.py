from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from iam.shared.domain import AggregateRoot

from .events import (
    EmailVerificationCreated,
    EmailVerificationVerified,
)
from .exceptions import (
    EmailVerificationAlreadyVerifiedError,
    EmailVerificationExpiredError,
)
from .value_objects import EmailVerificationId, EmailVerificationTokenHash, UserId


@dataclass(slots=True)
class EmailVerification(
    AggregateRoot[EmailVerificationId],
):
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

        event = EmailVerificationCreated(
            verification_id=verification.id,
            user_id=verification.user_id,
            expires_at=verification.expires_at,
        )
        verification.record_event(event)

        return verification

    @property
    def is_verified(self) -> bool:
        return self.verified_at is not None

    def is_expired(
        self,
        now: datetime,
    ) -> bool:
        return now >= self.expires_at

    def mark_verified(
        self,
        *,
        verified_at: datetime,
    ):
        if self.is_verified:
            raise EmailVerificationAlreadyVerifiedError()

        if self.is_expired(now=verified_at):
            raise EmailVerificationExpiredError()

        self.verified_at = verified_at

        event = EmailVerificationVerified(
            verification_id=self.id,
            user_id=self.user_id,
            verified_at=verified_at,
        )
        self.record_event(event)
