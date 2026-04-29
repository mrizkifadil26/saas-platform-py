from billing.shared.exceptions import DomainError


class PaymentError(DomainError):
    """Base exception for payment-related errors."""


class InvalidPaymentStateError(PaymentError):
    """Raised when an operation is attempted on a payment in an invalid state."""


class InvalidPaymentAmountError(PaymentError):
    """Raised when an invalid payment amount is provided (e.g., negative amount)."""


class PaymentAlreadySucceededError(PaymentError):
    """Raised when an operation is attempted on a payment that has already succeeded."""


class PaymentAlreadyRefundedError(PaymentError):
    """Raised when an operation is attempted on a payment that has already been refunded."""
