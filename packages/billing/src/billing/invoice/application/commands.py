from __future__ import annotations

from dataclasses import dataclass

from billing.invoice.domain.value_objects.invoice_id import InvoiceId
from billing.shared.domain.value_objects.money import Money
from billing.shared.domain.value_objects.user_id import UserId


@dataclass(frozen=True, slots=True)
class CreateInvoiceLineCommand:
    description: str
    quantity: int
    unit_price: Money


@dataclass(frozen=True, slots=True)
class CreateInvoiceCommand:
    # TODO: later should we use customer_id than user_id
    user_id: UserId
    lines: tuple[CreateInvoiceLineCommand, ...]
    auto_issue: bool = False


@dataclass(frozen=True, slots=True)
class IssueInvoiceCommand:
    invoice_id: InvoiceId


@dataclass(frozen=True, slots=True)
class MarkInvoicePaidCommand:
    invoice_id: InvoiceId


@dataclass(frozen=True, slots=True)
class VoidInvoiceCommand:
    invoice_id: InvoiceId


@dataclass(frozen=True, slots=True)
class MarkInvoiceUncollectibleCommand:
    invoice_id: InvoiceId
