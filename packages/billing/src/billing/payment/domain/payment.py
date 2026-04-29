from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from billing.payment.domain.exceptions import (
    InvalidPaymentStateError,
    PaymentAlreadyRefundedError,
    PaymentAlreadySucceededError,
)
from billing.payment.domain.payment_events import (
    PaymentCanceled,
    PaymentCreated,
    PaymentFailed,
    PaymentProcessingStarted,
    PaymentRefunded,
    PaymentSucceeded,
)
from billing.payment.domain.payment_gateway import PaymentId
from billing.payment.domain.payment_status import PaymentStatus
from billing.payment.domain.value_objects.payment_method import PaymentMethod
from billing.shared.domain.aggregate_root import AggregateRoot
from billing.shared.domain.value_objects.money import Money
from billing.shared.domain.value_objects.user_id import UserId


@dataclass(slots=True)
class Payment(AggregateRoot[PaymentId]):
    """Aggregate root representing a payment."""

    id: PaymentId
    # TODO: later should use customer_id instead of user_id
    user_id: UserId
    # TODO: later should use invoiceId instead of str
    invoice_id: str

    amount: Money
    method: PaymentMethod
    status: PaymentStatus
    created_at: datetime

    gateway_reference: str | None = None
    failure_reason: str | None = None

    processing_started_at: datetime | None = None
    succeeded_at: datetime | None = None
    failed_at: datetime | None = None
    canceled_at: datetime | None = None
    refunded_at: datetime | None = None

    @classmethod
    def create(
        cls,
        id: PaymentId,
        user_id: UserId,
        invoice_id: str,
        amount: Money,
        method: PaymentMethod,
        created_at: datetime,
    ) -> Payment:
        if amount.amount <= 0:
            raise ValueError("Payment amount must be greater than zero.")

        payment = cls(
            id=id,
            user_id=user_id,
            invoice_id=invoice_id,
            amount=amount,
            method=method,
            status=PaymentStatus.PENDING,
            created_at=created_at,
        )

        event = PaymentCreated(
            payment_id=payment.id,
            user_id=payment.user_id,
            invoice_id=payment.invoice_id,
            amount=payment.amount,
        )
        payment.record_event(event)

        return payment

    def start_processing(
        self,
        *,
        occured_at: datetime,
    ) -> None:
        if not self.status.can_start_processing():
            raise InvalidPaymentStateError(
                f"Cannot start processing payment in state: {self.status}"
            )

        self.status = PaymentStatus.PROCESSING
        self.processing_started_at = occured_at

        event = PaymentProcessingStarted(
            payment_id=self.id,
            user_id=self.user_id,
            invoice_id=self.invoice_id,
        )
        self.record_event(event)

    def mark_succeeded(
        self,
        *,
        gateway_reference: str,
        occured_at: datetime,
    ) -> None:
        if self.status is PaymentStatus.SUCCEEDED:
            raise PaymentAlreadySucceededError(f"Payment already succeeded: {self.id}")

        if not self.status.can_succeed():
            raise InvalidPaymentStateError(
                f"Cannot mark payment as succeeded in state: {self.status}"
            )

        self.status = PaymentStatus.SUCCEEDED
        self.gateway_reference = gateway_reference
        self.succeeded_at = occured_at

        event = PaymentSucceeded(
            payment_id=self.id,
            user_id=self.user_id,
            invoice_id=self.invoice_id,
            gateway_reference=gateway_reference,
        )
        self.record_event(event)

    def mark_failed(
        self,
        *,
        reason: str,
        occurred_at: datetime,
    ) -> None:
        if not self.status.can_fail():
            raise InvalidPaymentStateError(
                f"Cannot fail payment from state: {self.status}"
            )

        if not reason.strip():
            raise ValueError("Failure reason cannot be empty.")

        self.status = PaymentStatus.FAILED
        self.failure_reason = reason
        self.failed_at = occurred_at

        event = PaymentFailed(
            payment_id=self.id,
            user_id=self.user_id,
            invoice_id=self.invoice_id,
            reason=reason,
            occurred_at=occurred_at,
        )

        self.record_event(event)

    def cancel(
        self,
        *,
        occurred_at: datetime,
    ) -> None:
        if not self.status.can_cancel():
            raise InvalidPaymentStateError(
                f"Cannot cancel payment from state: {self.status}"
            )

        self.status = PaymentStatus.CANCELED
        self.canceled_at = occurred_at

        event = PaymentCanceled(
            payment_id=self.id,
            user_id=self.user_id,
            invoice_id=self.invoice_id,
            occurred_at=occurred_at,
        )
        self.record_event(event)

    def refund(
        self,
        *,
        occurred_at: datetime,
    ) -> None:
        if self.status is PaymentStatus.REFUNDED:
            raise PaymentAlreadyRefundedError(f"Payment already refunded: {self.id}")

        if not self.status.can_refund():
            raise InvalidPaymentStateError(
                f"Cannot refund payment from state: {self.status}"
            )

        self.status = PaymentStatus.REFUNDED
        self.refunded_at = occurred_at

        event = PaymentRefunded(
            payment_id=self.id,
            user_id=self.user_id,
            invoice_id=self.invoice_id,
            occurred_at=occurred_at,
        )
        self.record_event(event)

    @property
    def is_successful(self) -> bool:
        return self.status is PaymentStatus.SUCCEEDED

    @property
    def is_terminal(self) -> bool:
        return self.status in {
            PaymentStatus.SUCCEEDED,
            PaymentStatus.FAILED,
            PaymentStatus.CANCELED,
            PaymentStatus.REFUNDED,
        }
