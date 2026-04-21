from billing.application.shared.exceptions import (
    ApplicationError,
)


class PaygApplicationError(ApplicationError):
    """Base exception for PAYG application services."""

    pass


class IdempotencyConflictError(PaygApplicationError):
    """Raised when an idempotent request conflicts with a previous request."""

    pass


class DuplicateRequestError(PaygApplicationError):
    """Raised when a request with the same idempotency key is already in progress."""

    pass
