from __future__ import annotations

from dataclasses import dataclass

from billing.invoice.domain.value_objects.invoice_id import InvoiceId
from billing.payment.domain.value_objects.payment_id import PaymentId
from billing.shared.domain.domain_event import DomainEvent
from billing.shared.domain.value_objects.money import Money
from billing.shared.domain.value_objects.user_id import UserId


@dataclass(frozen=True, slots=True)
class PaymentCreated(DomainEvent):
    payment_id: PaymentId
    # TODO: later we should use customer_id instead of user_id
    user_id: UserId
    invoice_id: InvoiceId
    amount: Money


@dataclass(frozen=True, slots=True)
class PaymentProcessingStarted(DomainEvent):
    payment_id: PaymentId
    # TODO: later we should use customer_id instead of user_id
    user_id: UserId
    invoice_id: InvoiceId


@dataclass(frozen=True, slots=True)
class PaymentSucceeded(DomainEvent):
    payment_id: PaymentId
    # TODO: later we should use customer_id instead of user_id
    user_id: UserId
    invoice_id: InvoiceId
    gateway_reference: str


@dataclass(frozen=True, slots=True)
class PaymentFailed(DomainEvent):
    payment_id: PaymentId
    # TODO: later we should use customer_id instead of user_id
    user_id: UserId
    invoice_id: InvoiceId
    reason: str


@dataclass(frozen=True, slots=True)
class PaymentCanceled(DomainEvent):
    payment_id: PaymentId
    # TODO: later we should use customer_id instead of user_id
    user_id: UserId
    invoice_id: InvoiceId


@dataclass(frozen=True, slots=True)
class PaymentRefunded(DomainEvent):
    payment_id: PaymentId
    # TODO: later we should use customer_id instead of user_id
    user_id: UserId
    invoice_id: InvoiceId
