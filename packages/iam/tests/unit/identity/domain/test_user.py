from datetime import datetime, timezone

import pytest

from iam.identity.domain import User, UserStatus
from iam.identity.domain.events import (
    UserActivated,
    UserDisabled,
    UserEmailChanged,
    UserEmailVerified,
    UserLocked,
    UserRegistered,
    UserUnlocked,
)
from iam.identity.domain.exceptions import (
    InvalidUserStateError,
    UserEmailAlreadyVerifiedError,
    UserEmailUnchangedError,
    UserEmailVerificationBlockedError,
    UserLoginBlockedError,
)
from iam.identity.domain.user import UserSuspended, UserUnsuspended
from iam.identity.domain.value_objects import Email


def make_email() -> Email:
    return Email("john@example.com")


def make_datetime() -> datetime:
    return datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )


def make_user(
    *,
    status: UserStatus = UserStatus.ACTIVE,
) -> User:
    now = make_datetime()

    return User(
        id=User.register(
            make_email(),
            registered_at=now,
        ).id,
        email=make_email(),
        status=status,
        created_at=now,
    )


class TestUserRegister:
    def test_register_creates_pending_user(self) -> None:
        registered_at = make_datetime()
        email = make_email()

        user = User.register(
            email=email,
            registered_at=registered_at,
        )

        assert user.id is not None
        assert user.email == email
        assert user.status == UserStatus.PENDING
        assert user.created_at == registered_at
        assert user.updated_at is None
        assert user.email_verified_at is None
        assert user.last_login_at is None

    def test_register_records_user_registered_event(self) -> None:
        registered_at = make_datetime()
        email = make_email()

        user = User.register(
            email=email,
            registered_at=registered_at,
        )

        (event,) = user.pull_events()

        assert isinstance(event, UserRegistered)
        assert event.user_id == user.id
        assert event.email == email


class TestUserEmailVerification:
    def test_is_email_verified_returns_false_when_not_verified(self) -> None:
        user = make_user()

        assert user.is_email_verified is False

    def test_is_email_verified_returns_true_when_verified(self) -> None:
        verified_at = make_datetime()
        user = make_user()

        user.mark_email_as_verified(
            verified_at=verified_at,
        )

        assert user.is_email_verified is True

    def test_mark_email_as_verified_marks_verified_and_records_event(self) -> None:
        verified_at = make_datetime()
        user = make_user()

        user.mark_email_as_verified(
            verified_at=verified_at,
        )

        assert user.email_verified_at == verified_at
        assert user.updated_at == verified_at
        assert user.is_email_verified is True

        (event,) = user.pull_events()

        assert isinstance(event, UserEmailVerified)
        assert event.user_id == user.id
        assert event.verified_at == verified_at

    def test_mark_email_as_verified_raises_when_already_verified(self) -> None:
        first_verified_at = make_datetime()
        second_verified_at = datetime(
            2026,
            1,
            2,
            tzinfo=timezone.utc,
        )

        user = make_user()

        user.mark_email_as_verified(
            verified_at=first_verified_at,
        )

        with pytest.raises(UserEmailAlreadyVerifiedError):
            user.mark_email_as_verified(
                verified_at=second_verified_at,
            )

    def test_mark_email_as_verified_raises_when_user_disabled(self) -> None:
        user = make_user(
            status=UserStatus.DISABLED,
        )

        with pytest.raises(
            UserEmailVerificationBlockedError,
        ):
            user.mark_email_as_verified(
                verified_at=make_datetime(),
            )


class TestUserActivate:
    def test_activate_activates_user_and_records_event(self) -> None:
        activated_at = make_datetime()
        user = make_user(
            status=UserStatus.PENDING,
        )

        user.activate(activated_at=activated_at)

        assert user.status == UserStatus.ACTIVE
        assert user.updated_at == activated_at

        (event,) = user.pull_events()

        assert isinstance(event, UserActivated)
        assert event.user_id == user.id
        assert event.activated_at == activated_at

    @pytest.mark.parametrize(
        "status",
        [
            UserStatus.ACTIVE,
            UserStatus.DISABLED,
            UserStatus.LOCKED,
            UserStatus.SUSPENDED,
        ],
    )
    def test_activate_raises_for_invalid_status(
        self,
        status: UserStatus,
    ) -> None:
        user = make_user(status=status)

        with pytest.raises(
            InvalidUserStateError,
            match="User is not eligible for activation",
        ):
            user.activate(activated_at=make_datetime())


class TestUserDisable:
    def test_disable_changes_status_and_records_event(self) -> None:
        disabled_at = make_datetime()
        user = make_user()

        user.disable(
            disabled_at=disabled_at,
        )

        assert user.status == UserStatus.DISABLED
        assert user.updated_at == disabled_at

        (event,) = user.pull_events()

        assert isinstance(event, UserDisabled)
        assert event.user_id == user.id

    @pytest.mark.parametrize("status", [UserStatus.DISABLED])
    def test_disable_raises_for_invalid_status(
        self,
        status: UserStatus,
    ) -> None:
        user = make_user(status=status)

        with pytest.raises(
            InvalidUserStateError,
            match="User is already disabled",
        ):
            user.disable(disabled_at=make_datetime())


class TestUserLock:
    def test_lock_changes_status_and_records_event(self) -> None:
        locked_at = make_datetime()
        user = make_user()

        user.lock(locked_at=locked_at)

        assert user.status == UserStatus.LOCKED
        assert user.updated_at == locked_at

        (event,) = user.pull_events()

        assert isinstance(event, UserLocked)
        assert event.user_id == user.id
        assert event.locked_at == locked_at

    @pytest.mark.parametrize(
        "status",
        [
            UserStatus.PENDING,
            UserStatus.DISABLED,
            UserStatus.LOCKED,
            UserStatus.SUSPENDED,
        ],
    )
    def test_lock_raises_for_invalid_status(
        self,
        status: UserStatus,
    ) -> None:
        user = make_user(status=status)

        with pytest.raises(
            InvalidUserStateError,
            match="User cannot be locked",
        ):
            user.lock(locked_at=make_datetime())


class TestUserUnlock:
    def test_unlock_changes_status_to_active_and_records_event(self) -> None:
        unlocked_at = make_datetime()
        user = make_user(
            status=UserStatus.LOCKED,
        )

        user.unlock(unlocked_at=unlocked_at)

        assert user.status == UserStatus.ACTIVE
        assert user.updated_at == unlocked_at

        (event,) = user.pull_events()

        assert isinstance(event, UserUnlocked)
        assert event.user_id == user.id
        assert event.unlocked_at == unlocked_at

    @pytest.mark.parametrize(
        "status",
        [
            UserStatus.PENDING,
            UserStatus.ACTIVE,
            UserStatus.DISABLED,
            UserStatus.SUSPENDED,
        ],
    )
    def test_unlock_raises_for_invalid_status(
        self,
        status: UserStatus,
    ) -> None:
        user = make_user(status=status)

        with pytest.raises(
            InvalidUserStateError,
            match="User is not locked",
        ):
            user.unlock(unlocked_at=make_datetime())


class TestUserSuspend:
    def test_suspend_changes_status_and_records_event(self) -> None:
        suspended_at = make_datetime()
        user = make_user()

        user.suspend(suspended_at=suspended_at)

        assert user.status == UserStatus.SUSPENDED
        assert user.updated_at == suspended_at

        (event,) = user.pull_events()

        assert isinstance(event, UserSuspended)
        assert event.user_id == user.id
        assert event.suspended_at == suspended_at

    @pytest.mark.parametrize(
        "status",
        [
            UserStatus.PENDING,
            UserStatus.SUSPENDED,
            UserStatus.DISABLED,
            UserStatus.LOCKED,
        ],
    )
    def test_suspend_raises_for_invalid_status(
        self,
        status: UserStatus,
    ) -> None:
        user = make_user(status=status)

        with pytest.raises(
            InvalidUserStateError,
            match="User cannot be suspended",
        ):
            user.suspend(suspended_at=make_datetime())


class TestUserUnsuspend:
    def test_unsuspend_changes_status_to_active_and_records_event(self) -> None:
        unsuspended_at = make_datetime()
        user = make_user(
            status=UserStatus.SUSPENDED,
        )

        user.unsuspend(unsuspended_at=unsuspended_at)

        assert user.status == UserStatus.ACTIVE
        assert user.updated_at == unsuspended_at

        (event,) = user.pull_events()

        assert isinstance(event, UserUnsuspended)
        assert event.user_id == user.id
        assert event.unsuspended_at == unsuspended_at

    @pytest.mark.parametrize(
        "status",
        [
            UserStatus.PENDING,
            UserStatus.ACTIVE,
            UserStatus.DISABLED,
            UserStatus.LOCKED,
        ],
    )
    def test_unsuspend_raises_for_invalid_status(
        self,
        status: UserStatus,
    ) -> None:
        user = make_user(status=status)

        with pytest.raises(
            InvalidUserStateError,
            match="User is not suspended",
        ):
            user.unsuspend(unsuspended_at=make_datetime())


class TestUserChangeEmail:
    def test_change_email_updates_email_and_records_event(self) -> None:
        changed_at = make_datetime()
        user = make_user()

        previous_email = user.email

        new_email = Email("new@example.com")
        user.change_email(new_email, changed_at=changed_at)

        assert user.email == new_email
        assert user.updated_at == changed_at

        (event,) = user.pull_events()

        assert isinstance(event, UserEmailChanged)
        assert event.user_id == user.id
        assert event.new_email == new_email
        assert event.previous_email == previous_email
        assert event.changed_at == changed_at

    def test_change_email_raises_when_same_email(self) -> None:
        user = make_user()

        with pytest.raises(
            UserEmailUnchangedError,
        ):
            user.change_email(
                new_email=user.email,
                changed_at=make_datetime(),
            )


class TestUserLogin:
    def test_mark_login_sets_last_login_at(self) -> None:
        logged_in_at = make_datetime()
        user = make_user()

        user.mark_login(logged_in_at=logged_in_at)

        assert user.last_login_at == logged_in_at
        assert user.updated_at == logged_in_at

    @pytest.mark.parametrize(
        "status",
        [
            UserStatus.DISABLED,
            UserStatus.LOCKED,
            UserStatus.SUSPENDED,
        ],
    )
    def test_mark_login_raises_when_login_blocked(
        self,
        status: UserStatus,
    ) -> None:
        user = make_user(status=status)

        with pytest.raises(
            UserLoginBlockedError,
        ):
            user.mark_login(
                logged_in_at=make_datetime(),
            )


class TestUserTouch:
    def test_touch_updates_updated_at(self) -> None:
        user = make_user()
        now = make_datetime()

        user.touch(now)

        assert user.updated_at == now
