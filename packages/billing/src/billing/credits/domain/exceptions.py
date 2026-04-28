from billing.shared.exceptions import DomainError


class CreditError(DomainError):
    """Base exception for credit-related errors."""


class InvalidCreditsAmountError(CreditError):
    """Raised when an invalid credit amount is provided (e.g., negative amount)."""


class InsufficientCreditsError(CreditError):
    """Raised when an account does not have enough credits for a requested operation."""

    def __init__(self, *, requested: int, available: int) -> None:
        super().__init__(
            f"Insufficient credits: requested={requested}, available={available}"
        )
        self.requested = requested
        self.available = available


class InsufficientReservedCreditsError(CreditError):
    """Raised when reserved credits are insufficient."""

    def __init__(self, *, requested: int, reserved: int) -> None:
        super().__init__(
            f"Insufficient reserved credits: requested={requested}, reserved={reserved}"
        )
        self.requested = requested
        self.reserved = reserved


class CreditGrantExpiredError(CreditError):
    """Raised when an expired credit grant is used."""


class CreditGrantOverConsumedError(CreditError):
    """Raised when consuming more than the remaining credits in a grant."""

    def __init__(self, *, requested: int, remaining: int) -> None:
        super().__init__(
            f"Credit grant over-consumed: requested={requested}, remaining={remaining}"
        )
        self.requested = requested
        self.remaining = remaining


class CreditBalanceInconsistentError(CreditError):
    """Raised when balance and grant state are inconsistent."""


class CreditLedgerEntryError(CreditError):
    """Base exception for credit ledger entry errors."""


class InvalidCreditLedgerEntryError(CreditLedgerEntryError):
    """Raised when a credit ledger entry is invalid."""
