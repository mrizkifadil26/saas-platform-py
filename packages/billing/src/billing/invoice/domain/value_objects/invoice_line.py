from __future__ import annotations

from dataclasses import dataclass

from billing.invoice.domain.exceptions import InvalidInvoiceLineError
from billing.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class InvoiceLine:
    description: str
    quantity: int
    unit_price: Money

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise InvalidInvoiceLineError("Invoice line description cannot be empty.")

        if self.quantity <= 0:
            raise InvalidInvoiceLineError(
                "Invoice line quantity must be greater than zero."
            )

        if self.unit_price.amount < 0:
            raise InvalidInvoiceLineError("Invoice line unit price cannot be negative.")

    @property
    def total(self) -> Money:
        return self.unit_price.multiply(self.quantity)
