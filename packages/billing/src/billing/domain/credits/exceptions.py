from billing.domain.shared.exceptions import (
    BillingDomainError,
)


class CreditsDomainError(BillingDomainError):
    """Base exception for credits domain."""

    pass


class InsufficientCredits(CreditsDomainError):
    """Raised when a wallet does not have enough credits to cover a cost."""

    pass


class InvalidCreditsAmount(CreditsDomainError):
    """Raised when an invalid credits amount is provided (e.g., negative)."""

    pass
