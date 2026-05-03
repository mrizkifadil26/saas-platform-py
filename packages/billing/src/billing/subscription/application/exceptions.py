from billing.shared.exceptions import ApplicationError


class SubscriptionError(ApplicationError):
    """Base exception for subscription application services."""

    pass


class SubscriptionNotFoundError(SubscriptionError):
    """Raised when a subscription cannot be found."""

    pass


class ActiveSubscriptionAlreadyExistsError(SubscriptionError):
    """Raised when a subscription already exists for a user and plan."""

    pass
