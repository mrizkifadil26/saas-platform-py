class SubscriptionApplicationError(Exception):
    """Base exception for subscription application services."""

    pass


class SubscriptionNotFound(SubscriptionApplicationError):
    """Raised when a subscription cannot be found."""

    pass


class ActiveSubscriptionAlreadyExists(
    SubscriptionApplicationError
):
    """Raised when a subscription already exists for a user and plan."""

    pass


class IdempotencyConflict(SubscriptionApplicationError):
    """Raised when a request has already been processed."""

    pass
