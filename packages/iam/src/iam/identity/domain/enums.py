from enum import StrEnum


class UserStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    LOCKED = "locked"
    DISABLED = "disabled"
    SUSPENDED = "suspended"

    # State checks
    def is_pending(self) -> bool:
        """
        User registered but not fully activated yet.
        Usually waiting for email verification or approval.
        Authentication is blocked.
        """
        return self == UserStatus.PENDING

    def is_active(self) -> bool:
        """
        Fully operational state.
        User can authenticate and use the system normally.
        """
        return self == UserStatus.ACTIVE

    def is_locked(self) -> bool:
        """
        Temporary security restriction.
        Usually caused by failed logins or suspicious activity.
        """
        return self == UserStatus.LOCKED

    def is_disabled(self) -> bool:
        """
        Administrative deactivation.
        User access is fully blocked.
        TODO: later use manually re-enabled.
        """
        return self == UserStatus.DISABLED

    def is_suspended(self) -> bool:
        """
        Business or policy restriction.
        Often temporary and may allow limited visibility.
        """
        return self == UserStatus.SUSPENDED

    # Capability checks

    def can_authenticate(self) -> bool:
        """
        Determines whether login/authentication is allowed.
        """
        return self == UserStatus.ACTIVE

    def can_activate(self) -> bool:
        return self in {
            UserStatus.PENDING,
            UserStatus.LOCKED,
            UserStatus.SUSPENDED,
        }

    def can_lock(self) -> bool:
        return self.is_active()

    def can_unlock(self) -> bool:
        return self.is_locked()

    def can_disable(self) -> bool:
        return self in {
            UserStatus.PENDING,
            UserStatus.ACTIVE,
            UserStatus.LOCKED,
            UserStatus.SUSPENDED,
        }

    def can_suspend(self) -> bool:
        return self.is_active()

    def can_unsuspend(self) -> bool:
        return self.is_suspended()

    # Semantic checks
    def is_terminal(self) -> bool:
        return self.is_disabled()

    def is_operational(self) -> bool:
        return self in {
            UserStatus.ACTIVE,
            UserStatus.LOCKED,
            UserStatus.SUSPENDED,
        }

    def requires_attention(self) -> bool:
        return self in {
            UserStatus.PENDING,
            UserStatus.LOCKED,
            UserStatus.SUSPENDED,
        }

    def blocks_login(self) -> bool:
        return not self.can_authenticate()


class CredentialStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    COMPROMISED = "compromised"
