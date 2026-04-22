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


class DuplicateReference(CreditsDomainError):
    """Raised when a grant with the same reference ID already exists."""

    pass


class GrantNotAvailable(CreditsDomainError):
    """Raised when a grant is not active or has no remaining credits."""

    pass


class GrantNotActive(CreditsDomainError):
    """Raised when a grant is not active."""

    pass
