from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from billing.credits.domain.value_objects.credits import Credits
from billing.payg.domain.exceptions import (
    InvalidPaygPurchaseAmountError,
    InvalidPaygPurchaseStateError,
    PaygPurchaseAlreadyGrantedError,
)
from billing.payg.domain.payg_purchase_events import (
    PaygPurchaseCreated,
    PaygPurchaseCreditGranted,
    PaygPurchasePaymentFailed,
    PaygPurchasePaymentSucceeded,
    PaygPurchaseRefunded,
)
from billing.payg.domain.payg_purchase_status import PaygPurchaseStatus
from billing.payg.domain.value_objects.pack_code import PackCode
from billing.payg.domain.value_objects.payg_purchase_id import PaygPurchaseId
from billing.shared.domain.aggregate_root import AggregateRoot
from billing.shared.domain.value_objects.money import Money
from billing.shared.domain.value_objects.user_id import UserId


@dataclass(eq=False, slots=True)
class PaygPurchase(AggregateRoot[PaygPurchaseId]):
    id: PaygPurchaseId
    # TODO: later we should use customer_id instead of user_id, but for now we can use user_id since we don't have customer_id yet
    user_id: UserId
    # TODO: later we should use a better pricing model instead of pack_code and credits, but for now we can use it since it's simple and easy to understand
    pack_code: PackCode
    credits: Credits
    price: Money
    expires_in_days: int
    status: PaygPurchaseStatus
    created_at: datetime
    paid_at: datetime | None = None
    credits_granted_at: datetime | None = None
    failed_at: datetime | None = None
    refunded_at: datetime | None = None
    failure_reason: str | None = None

    @classmethod
    def create(
        cls,
        *,
        purchase_id: PaygPurchaseId,
        # TODO: later we should use customer_id instead of user_id, but for now we can use user_id since we don't have customer_id yet
        user_id: UserId,
        # TODO: later we should use a better pricing model instead of pack_code and credits, but for now we can use it since it's simple and easy to understand
        pack_code: PackCode,
        credits: Credits,
        price: Money,
        expires_in_days: int,
        occurred_at: datetime,
    ) -> PaygPurchase:
        if credits.amount <= 0:
            raise InvalidPaygPurchaseAmountError(
                "PAYG purchase credits must be greater than zero."
            )

        purchase = cls(
            id=purchase_id,
            user_id=user_id,
            pack_code=pack_code,
            credits=credits,
            price=price,
            expires_in_days=expires_in_days,
            status=PaygPurchaseStatus.PENDING,
            created_at=occurred_at,
        )

        event = PaygPurchaseCreated(
            purchase_id=purchase.id,
            user_id=purchase.user_id,
            credits=purchase.credits,
        )

        purchase.record_event(event)

        return purchase

    def mark_payment_succeeded(
        self,
        *,
        occurred_at: datetime,
    ) -> None:
        if not self.status.can_mark_payment_succeeded():
            raise InvalidPaygPurchaseStateError(
                f"Cannot mark payment succeeded from state: {self.status}"
            )

        self.status = PaygPurchaseStatus.PAYMENT_SUCCEEDED
        self.paid_at = occurred_at

        event = PaygPurchasePaymentSucceeded(
            purchase_id=self.id,
            user_id=self.user_id,
        )
        self.record_event(event)

    def mark_credits_granted(
        self,
        *,
        occurred_at: datetime,
    ) -> None:
        if self.status is PaygPurchaseStatus.CREDITS_GRANTED:
            raise PaygPurchaseAlreadyGrantedError(
                f"PAYG purchase already granted: {self.id}"
            )

        if not self.status.can_mark_credits_granted():
            raise InvalidPaygPurchaseStateError(
                f"Cannot grant credits from state: {self.status}"
            )

        self.status = PaygPurchaseStatus.CREDITS_GRANTED
        self.credits_granted_at = occurred_at

        event = PaygPurchaseCreditGranted(
            purchase_id=self.id,
            user_id=self.user_id,
            credits=self.credits,
        )
        self.record_event(event)

    def fail(
        self,
        *,
        reason: str,
        occurred_at: datetime,
    ) -> None:

        if not self.status.can_fail():
            raise InvalidPaygPurchaseStateError(
                f"Cannot fail PAYG purchase from state: {self.status}"
            )

        if not reason.strip():
            raise ValueError("Failure reason cannot be empty.")

        self.status = PaygPurchaseStatus.FAILED
        self.failed_at = occurred_at
        self.failure_reason = reason

        event = PaygPurchasePaymentFailed(
            purchase_id=self.id,
            user_id=self.user_id,
            failure_reason=reason,
        )
        self.record_event(event)

    def refund(
        self,
        *,
        occurred_at: datetime,
    ) -> None:
        if not self.status.can_refund():
            raise InvalidPaygPurchaseStateError(
                f"Cannot refund PAYG purchase from state: {self.status}"
            )

        self.status = PaygPurchaseStatus.REFUNDED
        self.refunded_at = occurred_at

        event = PaygPurchaseRefunded(
            purchase_id=self.id,
            user_id=self.user_id,
        )
        self.record_event(event)

    @property
    def is_paid(self) -> bool:
        return self.paid_at is not None

    @property
    def is_credits_granted(self) -> bool:
        return self.status is PaygPurchaseStatus.CREDITS_GRANTED
