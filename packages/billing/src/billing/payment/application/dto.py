from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from billing.payment.domain.payment import Payment


@dataclass(frozen=True, slots=True)
class PaymentDTO:
    id: str
    user_id: str
    invoice_id: str
    amount: Decimal
    currency: str
    method_type: str
    method_provider: str | None
    method_reference: str | None
    status: str
    gateway_reference: str | None
    failure_reason: str | None
    created_at: datetime
    processing_started_at: datetime | None
    succeeded_at: datetime | None
    failed_at: datetime | None
    canceled_at: datetime | None
    refunded_at: datetime | None

    @classmethod
    def from_domain(cls, payment: Payment) -> PaymentDTO:
        return cls(
            id=str(payment.id),
            user_id=str(payment.user_id),
            invoice_id=str(payment.invoice_id),
            amount=payment.amount.amount,
            currency=payment.amount.currency.value,
            method_type=payment.method.type.value,
            method_provider=payment.method.provider,
            method_reference=payment.method.reference,
            status=payment.status.value,
            gateway_reference=payment.gateway_reference,
            failure_reason=payment.failure_reason,
            created_at=payment.created_at,
            processing_started_at=payment.processing_started_at,
            succeeded_at=payment.succeeded_at,
            failed_at=payment.failed_at,
            canceled_at=payment.canceled_at,
            refunded_at=payment.refunded_at,
        )