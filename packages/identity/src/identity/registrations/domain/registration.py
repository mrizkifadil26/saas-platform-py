from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from identity.accounts.domain.value_objects import UserId
from identity.registrations.domain.policies import RegistrationPolicy
from identity.shared.domain.email import EmailAddress
from identity.shared.infrastructure.security.password.value_objects import PasswordHash
from identity.shared.kernel.aggregate_root import AggregateRoot

from .enums import RegistrationMethod, RegistrationStatus, RegistrationStep
from .exceptions import (
    RegistrationAlreadyCompletedError,
    RegistrationEmailAlreadyVerifiedError,
    RegistrationEmailNotSetError,
    RegistrationExpiredError,
    RegistrationNotCancellableError,
    RegistrationNotPendingError,
)
from .value_objects import RegistrationId


@dataclass(slots=True)
class Registration(AggregateRoot[RegistrationId]):
    method: RegistrationMethod
    status: RegistrationStatus
    step: RegistrationStep

    created_at: datetime
    updated_at: datetime
    expires_at: datetime

    email: EmailAddress | None = None
    password_hash: PasswordHash | None = None
    email_verified_at: datetime | None = None
    user_id: UserId | None = None

    completed_at: datetime | None = None

    @classmethod
    def create(
        cls,
        *,
        method: RegistrationMethod,
        created_at: datetime,
        expires_at: datetime,
    ) -> Registration:
        return Registration(
            id=RegistrationId.generate(),
            method=method,
            status=RegistrationStatus.PENDING,
            step=RegistrationStep.STARTED,
            expires_at=expires_at,
            created_at=created_at,
            updated_at=created_at,
        )

    @property
    def email_verified(self) -> bool:
        return self.email_verified_at is not None

    @property
    def password_configured(self) -> bool:
        return self.password_hash is not None

    @property
    def is_pending(self) -> bool:
        return self.status is RegistrationStatus.PENDING

    @property
    def is_completed(self) -> bool:
        return self.status is RegistrationStatus.COMPLETED

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

    def set_email(
        self,
        email: EmailAddress,
        *,
        now: datetime,
    ) -> None:
        if self.email_verified:
            raise RegistrationEmailAlreadyVerifiedError()

        self.email = email
        self.updated_at = now

    def verify_email(
        self,
        *,
        now: datetime,
    ) -> None:
        if self.email is None:
            raise RegistrationEmailNotSetError()

        if self.email_verified:
            raise RegistrationEmailAlreadyVerifiedError()

        self.email_verified_at = now
        self.updated_at = now

    def set_password(
        self,
        password_hash: PasswordHash,
        *,
        now: datetime,
    ) -> None:
        self.password_hash = password_hash
        self.updated_at = now

    def assign_user(
        self,
        user_id: UserId,
        *,
        now: datetime,
    ) -> None:
        self.user_id = user_id
        self.updated_at = now

    def require_email(self) -> EmailAddress:
        if self.email is None:
            raise RegistrationEmailNotSetError()

        return self.email

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
        if self.is_completed:
            raise RegistrationNotCancellableError()

        if self.is_expired_at(now=cancelled_at):
            raise RegistrationNotCancellableError()

        self.status = RegistrationStatus.CANCELLED
        self.cancelled_at = cancelled_at
        self.updated_at = cancelled_at
