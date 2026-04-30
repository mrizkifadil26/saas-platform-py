from billing.shared.exceptions import ApplicationError


class InvoiceApplicationError(ApplicationError):
    """Base class for all exceptions raised by the invoice application."""


class InvoiceNotFoundError(InvoiceApplicationError):
    """Raised when an invoice is not found."""
