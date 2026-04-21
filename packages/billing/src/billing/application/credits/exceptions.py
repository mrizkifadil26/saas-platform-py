from billing.application.shared.exceptions import (
    ApplicationError,
)


class CreditsApplicationError(ApplicationError):
    """Base exception for credits application errors."""


class IdempotencyConflictError(CreditsApplicationError):
    """Raised when a request with the same idempotency key has already been processed."""


class DuplicateRequestError(CreditsApplicationError):
    """Raised when a request with the same request ID has already been processed."""
