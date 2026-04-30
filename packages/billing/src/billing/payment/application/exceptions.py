from billing.shared.exceptions import ApplicationError


class PaymentApplicationError(ApplicationError):
    """Base class for all exceptions raised by the payment application."""


class PaymentNotFoundError(PaymentApplicationError):
    """Raised when a payment is not found."""


class InvoiceNotFoundError(PaymentApplicationError):
    """Raised when an invoice is not found."""


class InvoiceNotPayableError(PaymentApplicationError):
    """Raised when an invoice is not in a payable state."""


class PaymentGatewayError(PaymentApplicationError):
    """Raised when there is an error with the payment gateway."""
