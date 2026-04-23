from billing.domain.shared.exceptions import (
    BillingDomainError,
)


class PricingError(BillingDomainError):
    """Base exception for pricing-related errors."""

    pass


class InvalidPlanConfiguration(PricingError):
    """Base exception for pricing-related errors."""

    pass


class PricingNotFound(PricingError):
    """Raised when a pricing entity is not found."""

    pass


class DomainInvariantError(PricingError):
    """Raised when a domain invariant is violated."""

    pass
