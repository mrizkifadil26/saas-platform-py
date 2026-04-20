from billing.domain.shared.exceptions import (
    BillingDomainError,
)


class SubscriptionDomainError(BillingDomainError):
    """Base exception for subscription domain errors."""


class UnknownPlan(SubscriptionDomainError):
    """Raised when an unknown subscription plan code is used."""


class InvalidSubscriptionStatus(SubscriptionDomainError):
    """Raised when an invalid subscription status is encountered."""


class DuplicatePeriodGrant(SubscriptionDomainError):
    """Raised when a subscription period grant is duplicated."""
