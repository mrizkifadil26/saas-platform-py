from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from iam.shared.domain import AggregateRoot

from .enums import UserStatus
from .events import (
    UserActivated,
    UserDisabled,
    UserEmailChanged,
    UserEmailVerified,
    UserLocked,
    UserRegistered,
    UserSuspended,
    UserUnlocked,
    UserUnsuspended,
)
from .exceptions import (
    InvalidUserStateError,
    UserEmailAlreadyVerifiedError,
    UserEmailUnchangedError,
    UserEmailVerificationBlockedError,
    UserLoginBlockedError,
)
from .value_objects import Email, UserId


@dataclass(slots=True)
class User(AggregateRoot[UserId]):
    email: Email
    status: UserStatus

    created_at: datetime
    updated_at: datetime | None = None

    email_verified_at: datetime | None = None
    last_login_at: datetime | None = None

    @classmethod
    def register(
        cls,
        email: Email,
        *,
        registered_at: datetime,
    ) -> User:
        user = cls(
            id=UserId.generate(),
            email=email,
            status=UserStatus.PENDING,
            created_at=registered_at,
        )

        event = UserRegistered(
            user_id=user.id,
            email=email,
        )
        user.record_event(event)

        return user

    @property
    def is_email_verified(self) -> bool:
        return self.email_verified_at is not None

    def activate(
        self,
        *,
        activated_at: datetime,
    ) -> None:
        if not self.status.can_activate():
            raise InvalidUserStateError(
                "User is not eligible for activation",
            )

        self.status = UserStatus.ACTIVE
        self.touch(activated_at)

        event = UserActivated(
            user_id=self.id,
            activated_at=activated_at,
        )
        self.record_event(event)

    def disable(
        self,
        *,
        disabled_at: datetime,
    ) -> None:
        if not self.status.can_disable():
            raise InvalidUserStateError(
                "User is already disabled",
            )

        self.status = UserStatus.DISABLED
        self.touch(disabled_at)

        event = UserDisabled(
            user_id=self.id,
            disabled_at=disabled_at,
        )
        self.record_event(event)

    def lock(
        self,
        *,
        locked_at: datetime,
    ) -> None:
        if not self.status.can_lock():
            raise InvalidUserStateError(
                "User cannot be locked",
            )

        self.status = UserStatus.LOCKED
        self.touch(locked_at)

        event = UserLocked(
            user_id=self.id,
            locked_at=locked_at,
        )
        self.record_event(event)

    def unlock(
        self,
        *,
        unlocked_at: datetime,
    ) -> None:
        if not self.status.can_unlock():
            raise InvalidUserStateError(
                "User is not locked",
            )

        self.status = UserStatus.ACTIVE
        self.touch(unlocked_at)

        # TODO: record user unlocked event
        event = UserUnlocked(
            user_id=self.id,
            unlocked_at=unlocked_at,
        )
        self.record_event(event)

    def suspend(
        self,
        *,
        suspended_at: datetime,
    ) -> None:
        if not self.status.can_suspend():
            raise InvalidUserStateError(
                "User cannot be suspended",
            )

        self.status = UserStatus.SUSPENDED
        self.touch(suspended_at)

        event = UserSuspended(
            user_id=self.id,
            suspended_at=suspended_at,
        )
        self.record_event(event)

    def unsuspend(
        self,
        *,
        unsuspended_at: datetime,
    ) -> None:
        if not self.status.can_unsuspend():
            raise InvalidUserStateError(
                "User is not suspended",
            )

        self.status = UserStatus.ACTIVE
        self.touch(unsuspended_at)

        event = UserUnsuspended(
            user_id=self.id,
            unsuspended_at=unsuspended_at,
        )
        self.record_event(event)

    def mark_email_as_verified(
        self,
        *,
        verified_at: datetime,
    ) -> None:
        if self.is_email_verified:
            raise UserEmailAlreadyVerifiedError()

        if self.status.is_disabled():
            raise UserEmailVerificationBlockedError()

        self.email_verified_at = verified_at
        self.touch(verified_at)

        event = UserEmailVerified(
            user_id=self.id,
            verified_at=verified_at,
        )
        self.record_event(event)

    def change_email(
        self,
        new_email: Email,
        *,
        changed_at: datetime,
    ) -> None:
        if self.email == new_email:
            raise UserEmailUnchangedError()

        previous_email = self.email

        self.email = new_email
        self.touch(changed_at)

        event = UserEmailChanged(
            user_id=self.id,
            previous_email=previous_email,
            new_email=new_email,
            changed_at=changed_at,
        )
        self.record_event(event)

    def mark_login(
        self,
        *,
        logged_in_at: datetime,
    ) -> None:
        if self.status.blocks_login():
            raise UserLoginBlockedError()

        self.last_login_at = logged_in_at
        self.touch(logged_in_at)

    def touch(self, at: datetime) -> None:
        self.updated_at = at
