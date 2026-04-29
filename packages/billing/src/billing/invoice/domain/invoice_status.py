from __future__ import annotations

from enum import StrEnum


class InvoiceStatus(StrEnum):
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"

    def can_issue(self) -> bool:
        return self is InvoiceStatus.DRAFT

    def can_mark_paid(self) -> bool:
        return self is InvoiceStatus.OPEN

    def can_void(self) -> bool:
        return self in {
            InvoiceStatus.DRAFT,
            InvoiceStatus.OPEN,
        }

    def can_mark_uncollectible(self) -> bool:
        return self is InvoiceStatus.OPEN
