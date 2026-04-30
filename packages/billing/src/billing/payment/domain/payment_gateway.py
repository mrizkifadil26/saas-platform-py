from dataclasses import dataclass
from typing import Protocol

from billing.invoice.domain.value_objects.invoice_id import InvoiceId
from billing.payment.domain.value_objects.payment_id import PaymentId
from billing.payment.domain.value_objects.payment_method import PaymentMethod
from billing.shared.domain.value_objects.money import Money
from billing.shared.domain.value_objects.user_id import UserId


@dataclass(frozen=True, slots=True)
class ChargeRequest:
    payment_id: PaymentId
    # TODO: later we should use customer_id instead of user_id
    user_id: UserId
    invoice_id: InvoiceId
    amount: Money
    method: PaymentMethod
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class ChargeResult:
    succeeded: bool
    gateway_reference: str | None = None
    failure_reason: str | None = None


@dataclass(frozen=True, slots=True)
class RefundRequest:
    payment_id: PaymentId
    gateway_reference: str
    amount: Money
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RefundResult:
    succeeded: bool
    gateway_reference: str | None = None
    failure_reason: str | None = None


class PaymentGateway(Protocol):
    async def charge(self, request: ChargeRequest) -> ChargeResult:
        raise NotImplementedError

    async def refund(self, request: RefundRequest) -> RefundResult:
        raise NotImplementedError
