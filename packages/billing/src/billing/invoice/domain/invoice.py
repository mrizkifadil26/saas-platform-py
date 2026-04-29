from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from billing.invoice.domain.exceptions import (
    EmptyInvoiceError,
    InvalidInvoiceStateError,
    InvoiceAlreadyPaidError,
)
from billing.invoice.domain.invoice_events import (
    InvoiceCreated,
    InvoiceIssued,
    InvoiceMarkedUncollectible,
    InvoicePaid,
    InvoiceVoided,
)
from billing.invoice.domain.invoice_status import InvoiceStatus
from billing.invoice.domain.value_objects.invoice_id import InvoiceId
from billing.invoice.domain.value_objects.invoice_line import InvoiceLine
from billing.shared.domain.aggregate_root import AggregateRoot
from billing.shared.domain.value_objects.money import Money
from billing.shared.domain.value_objects.user_id import UserId


@dataclass(slots=True)
class Invoice(AggregateRoot[InvoiceId]):
    id: InvoiceId
    # TODO: later should use CustomerId instead of UserId
    user_id: UserId
    status: InvoiceStatus
    lines: list[InvoiceLine]
    created_at: datetime

    issued_at: datetime | None = None
    paid_at: datetime | None = None
    voided_at: datetime | None = None
    uncollectible_at: datetime | None = None

    @classmethod
    def create(
        cls,
        *,
        invoice_id: InvoiceId,
        user_id: UserId,
        lines: list[InvoiceLine],
        occurred_at: datetime,
    ) -> Invoice:
        if not lines:
            raise EmptyInvoiceError("Invoice must contain at least one line.")

        invoice = cls(
            id=invoice_id,
            user_id=user_id,
            status=InvoiceStatus.DRAFT,
            lines=list(lines),
            created_at=occurred_at,
        )

        event = InvoiceCreated(
            invoice_id=invoice_id,
            user_id=user_id,
            total=invoice.total,
            # occurred_at=occurred_at,
        )
        invoice.record_event(event)

        return invoice

    @property
    def total(self) -> Money:
        if not self.lines:
            raise EmptyInvoiceError("Invoice must contain at least one line.")

        total = self.lines[0].total

        for line in self.lines[1:]:
            total = total + line.total

        return total

    def issue(self, *, occurred_at: datetime) -> None:
        if not self.status.can_issue():
            raise InvalidInvoiceStateError(
                f"Cannot issue invoice from state: {self.status}"
            )

        if not self.lines:
            raise EmptyInvoiceError("Cannot issue invoice without lines.")

        self.status = InvoiceStatus.OPEN
        self.issued_at = occurred_at

        event = InvoiceIssued(
            invoice_id=self.id,
            user_id=self.user_id,
            total=self.total,
            # occurred_at=occurred_at,
        )
        self.record_event(event)

    def mark_paid(self, *, occurred_at: datetime) -> None:
        if self.status is InvoiceStatus.PAID:
            raise InvoiceAlreadyPaidError(f"Invoice already paid: {self.id}")

        if not self.status.can_mark_paid():
            raise InvalidInvoiceStateError(
                f"Cannot mark invoice paid from state: {self.status}"
            )

        self.status = InvoiceStatus.PAID
        self.paid_at = occurred_at

        event = InvoicePaid(
            invoice_id=self.id,
            user_id=self.user_id,
            total=self.total,
            # occurred_at=occurred_at,
        )
        self.record_event(event)

    def void(self, *, occurred_at: datetime) -> None:
        if not self.status.can_void():
            raise InvalidInvoiceStateError(
                f"Cannot void invoice from state: {self.status}"
            )

        self.status = InvoiceStatus.VOID
        self.voided_at = occurred_at

        event = InvoiceVoided(
            invoice_id=self.id,
            user_id=self.user_id,
            # occurred_at=occurred_at,
        )
        self.record_event(event)

    def mark_uncollectible(self, *, occurred_at: datetime) -> None:
        if not self.status.can_mark_uncollectible():
            raise InvalidInvoiceStateError(
                f"Cannot mark invoice uncollectible from state: {self.status}"
            )

        self.status = InvoiceStatus.UNCOLLECTIBLE
        self.uncollectible_at = occurred_at

        event = InvoiceMarkedUncollectible(
            invoice_id=self.id,
            user_id=self.user_id,
            # occurred_at=occurred_at,
        )
        self.record_event(event)

    @property
    def is_payable(self) -> bool:
        return self.status is InvoiceStatus.OPEN

    @property
    def is_terminal(self) -> bool:
        return self.status in {
            InvoiceStatus.PAID,
            InvoiceStatus.VOID,
            InvoiceStatus.UNCOLLECTIBLE,
        }
