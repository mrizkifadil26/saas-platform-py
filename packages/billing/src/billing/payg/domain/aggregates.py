from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from billing.domain.payg.events import (
    PaygPurchaseCreated,
    PaygPurchaseMarkedPaid,
)
from billing.domain.payg.exceptions import (
    PurchaseStateError,
)
from billing.domain.payg.value_objects import (
    Money,
    PackCode,
    PaygPurchaseId,
)
from billing.domain.shared.enums import PurchaseStatus
from billing.domain.shared.ids import UserId


@dataclass(eq=False, slots=True)
class PaygPurchase:
    purchase_id: PaygPurchaseId
    user_id: UserId
    pack_code: PackCode
    amount: Money
    status: PurchaseStatus = PurchaseStatus.PENDING
    paid_at: datetime | None = None
    _events: list[object] = field(
        default_factory=list, init=False, repr=False
    )
    # request_id: RequestId | None = None
    # metadata: dict[str, str] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        purchase_id: PaygPurchaseId,
        user_id: UserId,
        pack_code: PackCode,
        amount: Money,
    ) -> PaygPurchase:
        purchase = cls(
            purchase_id=purchase_id,
            user_id=user_id,
            pack_code=pack_code,
            amount=amount,
        )

        purchase._events.append(
            PaygPurchaseCreated(
                purchase_id=purchase.purchase_id,
                user_id=purchase.user_id,
                pack_code=purchase.pack_code,
            )
        )
        return purchase

    @property
    def events(self) -> tuple[object, ...]:
        return tuple(self._events)

    def pull_events(self) -> list[object]:
        events = list(self._events)
        self._events.clear()
        return events

    def mark_paid(self, paid_at: datetime) -> None:
        if self.status != PurchaseStatus.PENDING:
            raise PurchaseStateError(
                "only pending purchase can be paid"
            )

        self.status = PurchaseStatus.PAID
        self.paid_at = paid_at
        self._events.append(
            PaygPurchaseMarkedPaid(
                purchase_id=self.purchase_id,
                user_id=self.user_id,
                pack_code=self.pack_code,
                amount=self.amount,
                paid_at=self.paid_at,
            )
        )

    def mark_failed(self) -> None:
        if self.status != PurchaseStatus.PENDING:
            raise PurchaseStateError(
                "only pending payg purchases can be marked failed"
            )
        self.status = PurchaseStatus.FAILED

    def cancel(self) -> None:
        if self.status != PurchaseStatus.PENDING:
            raise PurchaseStateError(
                "only pending payg purchases can be canceled"
            )
        self.status = PurchaseStatus.CANCELED
