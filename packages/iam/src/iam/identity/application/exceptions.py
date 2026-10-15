class IdentityError(Exception):
    """Base exception for identity module"""


class UserAlreadyExistsError(IdentityError):
    """Raised when a user with the specified email already exists."""

    def __init__(self, email: str) -> None:
        super().__init__(f"User already exists: {email}")


class UserNotFoundError(IdentityError):
    """Raised when a user with the specified identifier does not exist."""


class InvalidCredentialsError(IdentityError):
    """Raised when a provided password does not meet security requirements."""


class InvalidEmailVerificationTokenError(IdentityError):
    """Raised when email verification token is invalid."""


class EmailVerificationExpiredError(IdentityError):
    """Raised when verification token has expired."""


class UserEmailAlreadyVerifiedError(IdentityError):
    """Raised when attempting to verify or resend verification for an already verified email."""
