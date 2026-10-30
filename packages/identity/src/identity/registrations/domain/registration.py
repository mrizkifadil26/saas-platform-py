from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from identity.accounts.domain.value_objects import UserId
from identity.shared.domain.email import EmailAddress
from identity.shared.infrastructure.security.password.value_objects import PasswordHash
from identity.shared.kernel.aggregate_root import AggregateRoot

from .enums import RegistrationMethod
from .exceptions import (
    RegistrationEmailAlreadyVerifiedError,
    RegistrationEmailNotSetError,
)
from .value_objects import RegistrationId


@dataclass(slots=True)
class Registration(AggregateRoot[RegistrationId]):
    method: RegistrationMethod

    created_at: datetime
    updated_at: datetime

    email: EmailAddress | None = None
    password_hash: PasswordHash | None = None
    email_verified_at: datetime | None = None
    user_id: UserId | None = None

    @classmethod
    def create(
        cls,
        *,
        method: RegistrationMethod,
        created_at: datetime,
    ) -> Registration:
        return Registration(
            id=RegistrationId.generate(),
            method=method,
            created_at=created_at,
            updated_at=created_at,
        )

    @property
    def email_verified(self) -> bool:
        return self.email_verified_at is not None

    @property
    def password_configured(self) -> bool:
        return self.password_hash is not None

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
