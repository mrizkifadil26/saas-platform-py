"""Authentication domain exceptions.

Defines custom exceptions for authentication and session handling.
"""


class AuthError(Exception):
    """Base exception for all authentication-related errors.

    All authentication domain exceptions should inherit from this class.
    """


class EmailAlreadyRegistered(AuthError):
    """Raised when attempting to register with an email that already exists."""


class InvalidCredentials(AuthError):
    """Raised when provided authentication credentials are invalid."""


class UserInactive(AuthError):
    """Raised when an inactive user attempts to authenticate."""


class SessionNotFound(AuthError):
    """Raised when the requested session does not exist."""


class SessionRevoked(AuthError):
    """Raised when the session has been revoked manually or by the system."""


class SessionExpired(AuthError):
    """Raised when the session has expired due to timeout."""


class InvalidAccessToken(AuthError):
    """Raised when an access token is invalid or expired."""
