from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from iam.accounts.domain.value_objects import UserId
from iam.shared.domain.email import EmailAddress
from iam.shared.infrastructure.security.password.value_objects import PasswordHash
from iam.shared.kernel.aggregate_root import AggregateRoot

from .enums import RegistrationMethod, RegistrationStatus, RegistrationStep
from .exceptions import (
    RegistrationAlreadyCancelledError,
    RegistrationAlreadyCompletedError,
    RegistrationCancelledError,
    RegistrationEmailAlreadyVerifiedError,
    RegistrationEmailNotSetError,
    RegistrationEmailNotVerifiedError,
    RegistrationExpiredError,
    RegistrationNotCancellableError,
    RegistrationNotCompletableError,
    RegistrationPasswordAlreadySetError,
    RegistrationPasswordNotSetError,
    RegistrationStepError,
)
from .value_objects import RegistrationId, ResumeTokenHash


@dataclass(slots=True)
class Registration(AggregateRoot[RegistrationId]):
    method: RegistrationMethod
    status: RegistrationStatus
    step: RegistrationStep

    email: EmailAddress | None

    resume_token_hash: ResumeTokenHash

    created_at: datetime
    updated_at: datetime
    expires_at: datetime

    user_id: UserId | None = None
    password_hash: PasswordHash | None = None
    email_verified_at: datetime | None = None

    completed_at: datetime | None = None
    cancelled_at: datetime | None = None

    @classmethod
    def create(
        cls,
        *,
        method: RegistrationMethod,
        email: EmailAddress | None,
        resume_token_hash: ResumeTokenHash,
        expires_at: datetime,
        created_at: datetime,
        updated_at: datetime,
    ) -> Registration:
        if method is RegistrationMethod.EMAIL:
            step = RegistrationStep.EMAIL_CHALLENGE
        elif method is RegistrationMethod.GOOGLE:
            step = RegistrationStep.GOOGLE_CHALLENGE
        else:
            raise ValueError(f"Unsupported registration method: {method}")

        return Registration(
            id=RegistrationId.generate(),
            method=method,
            status=RegistrationStatus.PENDING,
            step=step,
            email=email,
            resume_token_hash=resume_token_hash,
            expires_at=expires_at,
            created_at=created_at,
            updated_at=updated_at,
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

    @property
    def is_expired(self) -> bool:
        return self.status is RegistrationStatus.EXPIRED

    @property
    def email_verified(self) -> bool:
        return self.email_verified_at is not None

    @property
    def password_configured(self) -> bool:
        return self.password_hash is not None

    def is_expired_at(
        self,
        now: datetime,
    ) -> bool:
        return now >= self.expires_at

    def set_resume_token(
        self,
        token_hash: ResumeTokenHash,
        *,
        now: datetime,
    ) -> None:
        self.ensure_pending(now=now)

        self.resume_token_hash = token_hash
        self.updated_at = now

    def verify_email(
        self,
        *,
        now: datetime,
    ) -> None:
        self.ensure_pending(now=now)

        if self.email is None:
            raise RegistrationEmailNotSetError(self.id)

        if self.email_verified:
            raise RegistrationEmailAlreadyVerifiedError()

        if self.step is not RegistrationStep.EMAIL_CHALLENGE:
            raise RegistrationStepError(
                f"Cannot verify email from step {self.step}.",
            )

        self.email_verified_at = now
        self.step = RegistrationStep.PASSWORD_SETUP
        self.updated_at = now

    def set_email(
        self,
        email: EmailAddress,
        *,
        now: datetime,
    ) -> None:
        self.ensure_pending(now=now)

        if self.email_verified:
            raise RegistrationEmailAlreadyVerifiedError(self.id.value)

        self.email = email
        self.updated_at = now

    def set_password(
        self,
        password_hash: PasswordHash,
        *,
        now: datetime,
    ) -> None:
        self.ensure_pending(now=now)

        if not self.email_verified:
            raise RegistrationEmailNotVerifiedError(self.id.value)

        if self.password_configured:
            raise RegistrationPasswordAlreadySetError(self.id)

        if self.step is not RegistrationStep.PASSWORD_SETUP:
            raise RegistrationStepError(
                f"Cannot set password from step {self.step}.",
            )

        self.password_hash = password_hash
        self.step = RegistrationStep.COMPLETE
        self.updated_at = now

    def complete(
        self,
        *,
        user_id: UserId,
        completed_at: datetime,
    ) -> None:
        if self.is_completed:
            if self.user_id != user_id:
                raise RegistrationAlreadyCompletedError(self.id)

            return

        self.ensure_completable(now=completed_at)

        self.user_id = user_id
        self.status = RegistrationStatus.COMPLETED
        self.completed_at = completed_at
        self.updated_at = completed_at

    def cancel(
        self,
        *,
        cancelled_at: datetime,
    ) -> None:
        if self.status is RegistrationStatus.CANCELLED:
            raise RegistrationAlreadyCancelledError()

        if self.status is RegistrationStatus.COMPLETED:
            raise RegistrationNotCancellableError()

        if self.status is RegistrationStatus.EXPIRED:
            raise RegistrationNotCancellableError()

        self.status = RegistrationStatus.CANCELLED
        self.cancelled_at = cancelled_at
        self.updated_at = cancelled_at

    def expire(
        self,
        *,
        now: datetime,
    ) -> None:
        if self.status is not RegistrationStatus.PENDING:
            return

        if not self.is_expired_at(now):
            raise RegistrationExpiredError(self.id.value)

        self.status = RegistrationStatus.EXPIRED
        self.updated_at = now

    def ensure_pending(
        self,
        *,
        now: datetime,
    ) -> None:
        if self.is_cancelled:
            raise RegistrationCancelledError(self.id.value)

        if self.is_completed:
            raise RegistrationAlreadyCompletedError(self.id)

        if self.is_expired_at(now):
            raise RegistrationExpiredError(self.id.value)

        if not self.is_pending:
            raise RegistrationNotCompletableError(self.id.value)

    def ensure_completable(
        self,
        *,
        now: datetime,
    ) -> None:
        self.ensure_pending(now=now)

        if self.method is RegistrationMethod.EMAIL:
            if not self.email_verified:
                raise RegistrationEmailNotVerifiedError(self.id.value)

            if not self.password_configured:
                raise RegistrationPasswordNotSetError(self.id)

        elif self.method is RegistrationMethod.GOOGLE:
            pass

        if self.step is not RegistrationStep.COMPLETE:
            raise RegistrationNotCompletableError(self.id)

    def require_email(self) -> EmailAddress:
        if self.email is None:
            raise RegistrationEmailNotSetError(self.id)

        return self.email
