from billing.shared.exceptions import ApplicationError


class PaygApplicationError(ApplicationError):
    """Base exception for PAYG application services."""


class PaygPurchaseNotFoundError(PaygApplicationError):
    """Raised when PAYG purchase cannot be found."""


class PaygPackageNotFoundError(PaygApplicationError):
    """Raised when PAYG package cannot be found."""


class CreditAccountNotFoundError(PaygApplicationError):
    """Raised when user credit account cannot be found."""


class InvoiceNotFoundError(PaygApplicationError):
    """Raised when invoice cannot be found."""


class PaymentNotFoundError(PaygApplicationError):
    """Raised when payment cannot be found."""


class PaymentGatewayError(PaygApplicationError):
    """Raised when payment gateway fails unexpectedly."""
