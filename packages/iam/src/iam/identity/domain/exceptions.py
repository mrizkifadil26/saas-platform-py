from iam.shared.domain.exceptions import DomainError


class UserAlreadyExists(DomainError):
    """Raised when trying to register a user with an email that already exists."""


class InvalidUserStateError(DomainError):
    """Raised when a user operation is invalid for the current state."""


class UserLoginBlockedError(
    InvalidUserStateError,
):
    """Raised when the user is not allowed to sign in."""


class UserEmailAlreadyVerifiedError(
    InvalidUserStateError,
):
    """Raised when an already verified email is verified again."""


class UserEmailVerificationBlockedError(
    InvalidUserStateError,
):
    """Raised when email verification is blocked."""


class UserEmailUnchangedError(DomainError):
    """Raised when changing to the same email."""
