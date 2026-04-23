from billing.shared.exceptions import ApplicationError


class SubscriptionError(ApplicationError):
    """Base exception for subscription application services."""

    pass


class SubscriptionNotFound(SubscriptionError):
    """Raised when a subscription cannot be found."""

    pass


class ActiveSubscriptionAlreadyExists(SubscriptionError):
    """Raised when a subscription already exists for a user and plan."""

    pass


class IdempotencyConflict(SubscriptionError):
    """Raised when a request has already been processed."""

    pass
