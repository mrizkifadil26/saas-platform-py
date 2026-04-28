from billing.shared.exceptions import DomainError


class CreditError(DomainError):
    """Base exception for credit-related errors."""

    pass


class InsufficientCreditsError(CreditError):
    """Raised when an account does not have enough credits for a requested operation."""

    pass


class InvalidCreditAmountError(CreditError):
    """Raised when an invalid credit amount is provided (e.g., negative amount)."""

    pass


class InsufficientReservedCreditsError(CreditError):
    """Raised when reserved credits are insufficient."""


class CreditGrantExpiredError(CreditError):
    """Raised when an expired credit grant is used."""


class CreditGrantNotExpiredError(CreditError):
    """Raised when attempting to expire a grant that is not yet expired."""


class CreditGrantOverConsumedError(CreditError):
    """Raised when consuming more than the remaining credits in a grant."""


class CreditBalanceInconsistentError(CreditError):
    """Raised when balance and grant state are inconsistent."""
