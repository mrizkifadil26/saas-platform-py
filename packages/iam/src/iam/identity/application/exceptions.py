class IdentityError(Exception):
    """Base exception for identity module"""


class UserAlreadyExistsError(IdentityError):
    """Raised when a user with the specified email already exists."""

    def __init__(self, email: str) -> None:
        super().__init__(f"User already exists: {email}")


class UserNotFoundError(Exception):
    """Raised when a user with the specified identifier does not exist."""


class InvalidPasswordError(Exception):
    """Raised when a provided password does not meet security requirements."""


class InvalidEmailVerificationTokenError(Exception):
    """Raised when email verification token is invalid."""


class EmailVerificationExpiredError(Exception):
    """Raised when verification token has expired."""


class UserEmailAlreadyVerifiedError(Exception):
    """Raised when attempting to verify or resend verification for an already verified email."""
