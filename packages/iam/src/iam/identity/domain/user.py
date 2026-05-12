from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from iam.shared.domain import AggregateRoot
from iam.shared.domain.exceptions import ValidationError

from .events import UserDisabled, UserRegistered
from .user_status import UserStatus
from .value_objects import EmailAddress, EmailVerification, UserId


@dataclass(slots=True)
class User(AggregateRoot[UserId]):
    email: EmailAddress
    verification: EmailVerification

    status: UserStatus

    created_at: datetime
    updated_at: datetime | None = None

    last_login_at: datetime | None = None

    @classmethod
    def register(
        cls,
        email: EmailAddress,
        *,
        registered_at: datetime,
    ) -> User:
        user = cls(
            id=UserId.generate(),
            email=email,
            verification=EmailVerification(),
            status=UserStatus.PENDING,
            created_at=registered_at,
        )

        event = UserRegistered(
            user_id=user.id,
            email=email.value,
        )
        user.record_event(event)

        return user

    def activate(
        self,
        *,
        activated_at: datetime,
    ) -> None:
        if not self.status.can_activate():
            raise ValidationError("User already active or invalid state")

        if not self.verification.is_verified:
            raise ValidationError("Email must be verified before activation")

        self.status = UserStatus.ACTIVE
        self.touch(activated_at)

        # TODO: record user activated event
        # self.record_event(
        #     UserActivated(user_id=self.id)
        # )

    def disable(
        self,
        *,
        disabled_at: datetime,
    ) -> None:
        if not self.status.can_disable():
            raise ValidationError(f"Cannot disable user from '{self.status}'")

        self.status = UserStatus.DISABLED
        self.touch(disabled_at)

        event = UserDisabled(user_id=self.id)
        self.record_event(event)

    def lock(self, *, locked_at: datetime) -> None:
        if not self.status.can_lock():
            raise ValidationError(
                f"Cannot lock user from '{self.status}'",
            )

        self.status = UserStatus.LOCKED
        self.touch(locked_at)

        # TODO: record user locked event
        # self.record_event(
        #     UserLocked(user_id=self.id)
        # )

    def unlock(self, *, unlocked_at: datetime) -> None:
        if not self.status.can_unlock():
            raise ValidationError(f"Cannot unlock user from '{self.status}'")

        self.status = UserStatus.ACTIVE
        self.touch(unlocked_at)

        # TODO: record user unlocked event
        # self.record_event(
        #     UserUnlocked(user_id=self.id)
        # )

    def suspend(self, *, suspended_at: datetime) -> None:
        if not self.status.can_suspend():
            raise ValidationError(f"Cannot suspend user from '{self.status}'")

        self.status = UserStatus.SUSPENDED
        self.touch(suspended_at)

        # TODO: record user suspended event
        # self.record_event(
        #     UserSuspended(user_id=self.id)
        # )

    def unsuspend(self, *, unsuspended_at: datetime) -> None:
        if not self.status.can_unsuspend():
            raise ValidationError(f"Cannot unsuspend user from '{self.status}'")

        self.status = UserStatus.ACTIVE
        self.touch(unsuspended_at)

        # TODO: record user unsuspended event
        # self.record_event(
        #     UserUnsuspended(user_id=self.id)
        # )

    def verify_email(
        self,
        *,
        verified_at: datetime,
    ) -> None:
        if self.verification.is_verified:
            raise ValidationError("Email already verified")

        if self.status.is_disabled():
            raise ValidationError("Disabled user cannot verify email")

        self.verification = self.verification.verify(
            verified_at=verified_at,
        )

        # TODO: record email verified event

    def change_email(
        self,
        new_email: EmailAddress,
        *,
        changed_at: datetime,
    ) -> None:
        if self.email == new_email:
            raise ValidationError("New email is the same as the current email")

        self.email = new_email
        self.touch(changed_at)

        # TODO: record email changed event

    def mark_login(
        self,
        *,
        logged_in_at: datetime,
    ) -> None:
        if self.status.blocks_login():
            raise ValidationError(
                f"Cannot login with user status '{self.status}'",
            )

        self.last_login_at = logged_in_at
        self.touch(logged_in_at)

    def touch(self, at: datetime) -> None:
        self.updated_at = at
