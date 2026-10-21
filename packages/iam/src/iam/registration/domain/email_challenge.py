from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from iam.registration.domain.enums import EmailChallengePurpose
from iam.shared.kernel import AggregateRoot

from .events import EmailChallengeCompleted, EmailChallengeCreated
from .exceptions import (
    EmailChallengeRevokedError,
    EmailVerificationAlreadyVerifiedError,
    EmailVerificationExpiredError,
)
from .value_objects import EmailChallengeId, EmailChallengeTokenHash, RegistrationId


@dataclass(slots=True)
class EmailChallenge(
    AggregateRoot[EmailChallengeId],
):
    registration_id: RegistrationId
    token_hash: EmailChallengeTokenHash
    purpose: EmailChallengePurpose

    created_at: datetime
    expires_at: datetime

    revoked_at: datetime | None = None
    completed_at: datetime | None = None

    @classmethod
    def create(
        cls,
        *,
        registration_id: RegistrationId,
        token_hash: EmailChallengeTokenHash,
        purpose: EmailChallengePurpose,
        created_at: datetime,
        expires_at: datetime,
    ) -> EmailChallenge:
        challenge = cls(
            id=EmailChallengeId.generate(),
            registration_id=registration_id,
            purpose=purpose,
            token_hash=token_hash,
            created_at=created_at,
            expires_at=expires_at,
        )

        challenge.record_event(
            EmailChallengeCreated(
                challenge_id=challenge.id,
                registration_id=challenge.registration_id,
                expires_at=challenge.expires_at,
            ),
        )

        return challenge

    @property
    def is_completed(self) -> bool:
        return self.completed_at is not None

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    def is_expired_at(
        self,
        *,
        now: datetime,
    ) -> bool:
        return now >= self.expires_at

    def revoke(
        self,
        *,
        revoked_at: datetime,
    ) -> None:
        if self.is_completed:
            return

        if self.is_revoked:
            return

        self.revoked_at = revoked_at

    def complete(
        self,
        *,
        completed_at: datetime,
    ) -> None:
        if self.is_completed:
            raise EmailVerificationAlreadyVerifiedError(self.id)

        if self.is_revoked:
            raise EmailChallengeRevokedError(self.id)

        if self.is_expired_at(now=completed_at):
            raise EmailVerificationExpiredError(self.id)

        self.completed_at = completed_at

        self.record_event(
            EmailChallengeCompleted(
                challenge_id=self.id,
                registration_id=self.registration_id,
                completed_at=completed_at,
            ),
        )
