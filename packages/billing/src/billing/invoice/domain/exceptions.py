from __future__ import annotations

from billing.shared.exceptions import DomainError


class InvoiceError(DomainError):
    """Base exception for invoice domain errors."""


class InvalidInvoiceStateError(InvoiceError):
    """Raised when an invoice transition is invalid."""


class InvalidInvoiceLineError(InvoiceError):
    """Raised when an invoice line is invalid."""


class EmptyInvoiceError(InvoiceError):
    """Raised when an invoice has no lines."""


class InvoiceAlreadyPaidError(InvoiceError):
    """Raised when an already-paid invoice is marked paid again."""
