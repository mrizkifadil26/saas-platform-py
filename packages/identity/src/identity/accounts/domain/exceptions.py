from identity.shared.kernel.exceptions import DomainError


class AccountError(DomainError):
    """"""


class UserAlreadyExists(AccountError):
    """Raised when trying to register a user with an email that already exists."""


class InvalidUserStateError(AccountError):
    """Raised when a user operation is invalid for the current state."""


class UserLoginBlockedError(
    InvalidUserStateError,
):
    """Raised when the user is not allowed to sign in."""


class UserEmailUnchangedError(AccountError):
    """Raised when changing to the same email."""
