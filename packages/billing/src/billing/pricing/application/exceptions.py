from billing.shared.exceptions import ApplicationError


class PricingApplicationError(ApplicationError):
    """Base exception for pricing-related application errors."""

    pass


class PricingRuleNotFound(PricingApplicationError):
    """Raised when a pricing rule is not found."""

    pass
