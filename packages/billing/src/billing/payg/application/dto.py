from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from billing.payg.domain.payg_purchase import PaygPurchase


@dataclass(frozen=True, slots=True)
class PaygPurchaseDTO:
    id: str
    user_id: str
    credits: int
    status: str
    created_at: datetime
    paid_at: datetime | None
    credits_granted_at: datetime | None
    failed_at: datetime | None
    refunded_at: datetime | None
    failure_reason: str | None

    @classmethod
    def from_domain(cls, purchase: PaygPurchase) -> PaygPurchaseDTO:
        return cls(
            id=str(purchase.id),
            user_id=str(purchase.user_id),
            credits=purchase.credits.amount,
            status=purchase.status.value,
            created_at=purchase.created_at,
            paid_at=purchase.paid_at,
            credits_granted_at=purchase.credits_granted_at,
            failed_at=purchase.failed_at,
            refunded_at=purchase.refunded_at,
            failure_reason=purchase.failure_reason,
        )


@dataclass(frozen=True, slots=True)
class PurchasePaygCreditsResultDTO:
    purchase: PaygPurchaseDTO
    invoice_id: str
    payment_id: str
    amount: Decimal
    currency: str
    gateway_reference: str | None
