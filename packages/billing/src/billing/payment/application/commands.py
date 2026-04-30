from __future__ import annotations

from dataclasses import dataclass

from billing.invoice.domain.value_objects.invoice_id import InvoiceId
from billing.payment.domain.value_objects.payment_id import PaymentId
from billing.payment.domain.value_objects.payment_method import PaymentMethod


@dataclass(frozen=True, slots=True)
class ChargeInvoiceCommand:
    invoice_id: InvoiceId
    payment_method: PaymentMethod
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class MarkPaymentSucceededCommand:
    payment_id: PaymentId
    gateway_reference: str


@dataclass(frozen=True, slots=True)
class MarkPaymentFailedCommand:
    payment_id: PaymentId
    reason: str


@dataclass(frozen=True, slots=True)
class CancelPaymentCommand:
    payment_id: PaymentId


@dataclass(frozen=True, slots=True)
class RefundPaymentCommand:
    payment_id: PaymentId
