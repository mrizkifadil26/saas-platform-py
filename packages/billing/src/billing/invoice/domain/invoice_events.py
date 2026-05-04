from __future__ import annotations

from dataclasses import dataclass

from billing.invoice.domain.value_objects.invoice_id import InvoiceId
from billing.shared.domain.domain_event import DomainEvent
from billing.shared.domain.value_objects.money import Money
from billing.shared.domain.value_objects.user_id import UserId

# TODO(billing-migration):
# - Replace user_id with customer_id once Customer owns billing identity.


@dataclass(frozen=True, slots=True)
class InvoiceCreated(DomainEvent):
    invoice_id: InvoiceId
    user_id: UserId
    total: Money


@dataclass(frozen=True, slots=True)
class InvoiceIssued(DomainEvent):
    invoice_id: InvoiceId
    user_id: UserId
    total: Money


@dataclass(frozen=True, slots=True)
class InvoicePaid(DomainEvent):
    invoice_id: InvoiceId
    user_id: UserId
    total: Money


@dataclass(frozen=True, slots=True)
class InvoiceVoided(DomainEvent):
    invoice_id: InvoiceId
    user_id: UserId


@dataclass(frozen=True, slots=True)
class InvoiceMarkedUncollectible(DomainEvent):
    invoice_id: InvoiceId
    user_id: UserId
