from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from identity.accounts.domain.value_objects import UserId
from identity.shared.domain.email import EmailAddress
from identity.shared.infrastructure.security.password.value_objects import PasswordHash

from .enums import (
    RegistrationMethod,
    RegistrationStatus,
    RegistrationStep,
)
from .exceptions import (
    RegistrationAlreadyCancelledError,
    RegistrationAlreadyCompletedError,
    RegistrationCancelledError,
    RegistrationExpiredError,
    RegistrationNotCancellableError,
    RegistrationNotPendingError,
)
from .policies import RegistrationPolicy
from .registration import Registration
from .value_objects import ResumeTokenHash


@dataclass(slots=True)
class RegistrationWorkflow:
    registration: Registration
    status: RegistrationStatus
    step: RegistrationStep

    resume_token_hash: ResumeTokenHash

    created_at: datetime
    updated_at: datetime
    expires_at: datetime

    completed_at: datetime | None = None
    cancelled_at: datetime | None = None

    @classmethod
    def start(
        cls,
        *,
        method: RegistrationMethod,
        email: EmailAddress,
        resume_token_hash: ResumeTokenHash,
        expires_at: datetime,
        started_at: datetime,
        policy: RegistrationPolicy,
    ) -> RegistrationWorkflow:
        registration = Registration.create(
            method=method,
            email=email,
            created_at=started_at,
            updated_at=started_at,
        )

        return cls(
            registration=registration,
            status=RegistrationStatus.PENDING,
            step=policy.initial_step(method=method),
            resume_token_hash=resume_token_hash,
            created_at=started_at,
            updated_at=started_at,
            expires_at=expires_at,
        )

    @property
    def is_pending(self) -> bool:
        return self.status is RegistrationStatus.PENDING

    @property
    def is_completed(self) -> bool:
        return self.status is RegistrationStatus.COMPLETED

    @property
    def is_cancelled(self) -> bool:
        return self.status is RegistrationStatus.CANCELLED

    def is_expired_at(
        self,
        *,
        now: datetime,
    ) -> bool:
        return self.is_pending and now >= self.expires_at

    def ensure_accessible(
        self,
        *,
        now: datetime,
    ) -> None:
        if self.is_cancelled:
            raise RegistrationCancelledError()

        if self.is_completed:
            raise RegistrationAlreadyCompletedError()

        if self.is_expired_at(now=now):
            raise RegistrationExpiredError()

        if not self.is_pending:
            raise RegistrationNotPendingError()

    def ensure_step(
        self,
        expected: RegistrationStep,
        *,
        now: datetime,
    ) -> None:
        self.ensure_accessible(now=now)

        if self.step is not expected:
            raise RegistrationNotPendingError()

    def set_resume_token(
        self,
        token_hash: ResumeTokenHash,
        *,
        now: datetime,
    ) -> None:
        self.ensure_accessible(now=now)

        self.resume_token_hash = token_hash
        self.updated_at = now

    def verify_email(
        self,
        *,
        registration: Registration,
        now: datetime,
        policy: RegistrationPolicy,
    ) -> None:
        self.ensure_step(
            RegistrationStep.EMAIL_CHALLENGE,
            now=now,
        )

        policy.ensure_can_verify_email(
            method=self.method,
            step=self.step,
        )

        registration.verify_email(now=now)

        self.step = RegistrationStep.PASSWORD_SETUP
        self.updated_at = now

    def set_password(
        self,
        *,
        registration: Registration,
        password_hash: PasswordHash,
        now: datetime,
        policy: RegistrationPolicy,
    ) -> None:
        self.ensure_step(
            RegistrationStep.PASSWORD_SETUP,
            now=now,
        )

        policy.ensure_can_set_password(
            method=self.method,
            step=self.step,
            email_verified=registration.email_verified,
            password_configured=registration.password_configured,
        )

        registration.set_password(
            password_hash,
            now=now,
        )

        self.step = RegistrationStep.COMPLETE
        self.updated_at = now

    def complete(
        self,
        *,
        registration: Registration,
        user_id: UserId,
        completed_at: datetime,
        policy: RegistrationPolicy,
    ) -> None:
        if self.is_completed:
            if registration.user_id != user_id:
                raise RegistrationAlreadyCompletedError()

            return

        self.ensure_accessible(now=completed_at)

        policy.ensure_can_complete(
            method=self.method,
            step=self.step,
            email_verified=registration.email_verified,
            password_configured=registration.password_configured,
        )

        registration.assign_user(
            user_id,
            now=completed_at,
        )

        self.status = RegistrationStatus.COMPLETED
        self.completed_at = completed_at
        self.updated_at = completed_at

    def cancel(
        self,
        *,
        cancelled_at: datetime,
    ) -> None:
        if self.is_cancelled:
            raise RegistrationAlreadyCancelledError()

        if self.is_completed:
            raise RegistrationNotCancellableError()

        if self.is_expired_at(now=cancelled_at):
            raise RegistrationNotCancellableError()

        self.status = RegistrationStatus.CANCELLED
        self.cancelled_at = cancelled_at
        self.updated_at = cancelled_at
