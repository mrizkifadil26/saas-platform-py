from billing.shared.exceptions import DomainError


class PaygPurchaseError(DomainError):
    """Base exception for Pay-as-you-go purchase errors."""


class InvalidPaygPurchaseStateError(PaygPurchaseError):
    """Raised when an invalid state transition is attempted on a Pay-as-you-go purchase."""


class InvalidPaygPurchaseAmountError(PaygPurchaseError):
    """Raised when an invalid amount of credits is used for a Pay-as-you-go purchase."""


class PaygPurchaseAlreadyGrantedError(PaygPurchaseError):
    """Raised when a Pay-as-you-go purchase has already been granted."""
