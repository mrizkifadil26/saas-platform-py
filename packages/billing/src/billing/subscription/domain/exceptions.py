from billing.shared.exceptions import DomainError


class SubscriptionError(DomainError):
    """Base exception for subscription domain errors."""


class InvalidSubscriptionStateError(SubscriptionError):
    """Raised when an operation is attempted on a subscription in an invalid state."""


class InvalidSubscriptionPeriodError(SubscriptionError):
    """Raised when the subscription period is invalid."""


class SubscriptionAlreadyCanceledError(SubscriptionError):
    """Raised when an attempt is made to cancel an already canceled subscription."""


class RecurringCreditsAlreadyGrantedError(SubscriptionError):
    """Raised when an attempt is made to grant recurring credits that have already been granted."""


class InvalidSubscriptionItemError(SubscriptionError):
    """Raised when an invalid subscription item is encountered."""
