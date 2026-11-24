from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from identity.registrations.domain.enums import EmailChallengeMethod, EmailChallengePurpose
from identity.shared.domain.email import EmailAddress
from identity.shared.kernel import AggregateRoot

from .events import EmailChallengeCompleted, EmailChallengeCreated
from .exceptions import (
    EmailChallengeAlreadyCompletedError,
    EmailChallengeExpiredError,
    EmailChallengeRevokedError,
    InvalidEmailChallengeMethodError,
)
from .value_objects import (
    EmailChallengeCodeHash,
    EmailChallengeId,
    EmailChallengeTokenHash,
    RegistrationId,
)


@dataclass(slots=True)
class EmailChallenge(
    AggregateRoot[EmailChallengeId],
):
    registration_id: RegistrationId
    email: EmailAddress

    method: EmailChallengeMethod

    token_hash: EmailChallengeTokenHash | None
    code_hash: EmailChallengeCodeHash | None
    attempts: int

    purpose: EmailChallengePurpose

    created_at: datetime
    expires_at: datetime

    completed_at: datetime | None = None
    revoked_at: datetime | None = None

    @classmethod
    def create(
        cls,
        *,
        registration_id: RegistrationId,
        email: EmailAddress,
        method: EmailChallengeMethod,
        code_hash: EmailChallengeCodeHash | None = None,
        token_hash: EmailChallengeTokenHash | None = None,
        purpose: EmailChallengePurpose,
        created_at: datetime,
        expires_at: datetime,
    ) -> EmailChallenge:
        if method is EmailChallengeMethod.LINK:
            if token_hash is None or code_hash is not None:
                raise ValueError(
                    "Link challenge requires token_hash and no code_hash",
                )

        elif method is EmailChallengeMethod.OTP:
            if code_hash is None or token_hash is not None:
                raise ValueError(
                    "OTP challenge requires code_hash and no token_hash",
                )

        challenge = cls(
            id=EmailChallengeId.generate(),
            registration_id=registration_id,
            email=email,
            method=method,
            token_hash=token_hash,
            code_hash=code_hash,
            attempts=0,
            purpose=purpose,
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
            raise EmailChallengeAlreadyCompletedError()

        if self.is_revoked:
            return

        self.revoked_at = revoked_at

    def record_attempt(self) -> None:
        if self.method is not EmailChallengeMethod.OTP:
            raise InvalidEmailChallengeMethodError()

        self.attempts += 1

    def complete(
        self,
        *,
        completed_at: datetime,
    ) -> None:
        if self.is_completed:
            raise EmailChallengeAlreadyCompletedError()

        if self.is_revoked:
            raise EmailChallengeRevokedError()

        if self.is_expired_at(now=completed_at):
            raise EmailChallengeExpiredError()

        self.completed_at = completed_at

        self.record_event(
            EmailChallengeCompleted(
                challenge_id=self.id,
                registration_id=self.registration_id,
                completed_at=completed_at,
            ),
        )
