from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from billing.invoice.domain.invoice import Invoice
from billing.invoice.domain.value_objects.invoice_line import InvoiceLine


@dataclass(frozen=True, slots=True)
class InvoiceDTO:
    id: str
    user_id: str
    status: str
    total_amount: Decimal
    currency: str
    lines: tuple[InvoiceLineDTO, ...]
    created_at: datetime
    issued_at: datetime | None
    paid_at: datetime | None
    voided_at: datetime | None
    uncollectible_at: datetime | None

    @classmethod
    def from_domain(cls, invoice: Invoice) -> InvoiceDTO:
        return cls(
            id=str(invoice.id),
            user_id=str(invoice.user_id),
            status=invoice.status.value,
            total_amount=invoice.total.amount,
            currency=invoice.total.currency.value,
            lines=tuple(InvoiceLineDTO.from_domain(line) for line in invoice.lines),
            created_at=invoice.created_at,
            issued_at=invoice.issued_at,
            paid_at=invoice.paid_at,
            voided_at=invoice.voided_at,
            uncollectible_at=invoice.uncollectible_at,
        )


@dataclass(frozen=True, slots=True)
class InvoiceLineDTO:
    description: str
    quantity: int
    unit_price_amount: Decimal
    currency: str
    total_amount: Decimal

    @classmethod
    def from_domain(cls, line: InvoiceLine) -> InvoiceLineDTO:
        return cls(
            description=line.description,
            quantity=line.quantity,
            unit_price_amount=line.unit_price.amount,
            currency=line.unit_price.currency.value,
            total_amount=line.total.amount,
        )
