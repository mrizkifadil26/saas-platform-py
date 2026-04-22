from dataclasses import dataclass
from datetime import datetime

from billing.domain.credits.value_objects import Credits
from billing.domain.payg.value_objects import (
    Money,
    PackCode,
    PaygPurchaseId,
)
from billing.domain.shared.events import DomainEvent
from billing.domain.shared.ids import RequestId, UserId

# @dataclass(frozen=True, slots=True)
# class PaygCreditsPurchased:
#     purchase_id: str
#     user_id: UserId
#     plan_code: PlanCode
#     credits: Credits
#     occurred_at: datetime
#     request_id: RequestId | None = None
#     metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PaygPurchaseCreated(DomainEvent):
    purchase_id: PaygPurchaseId
    user_id: UserId
    pack_code: PackCode


@dataclass(frozen=True, slots=True)
class PaygPurchaseMarkedPaid(DomainEvent):
    purchase_id: PaygPurchaseId
    user_id: UserId
    pack_code: PackCode
    amount: Money
    paid_at: datetime
    request_id: RequestId | None = None


@dataclass(frozen=True, slots=True)
class PaygCreditGrantRequested(DomainEvent):
    purchase_id: PaygPurchaseId
    user_id: UserId
    pack_code: PackCode
    credits: Credits
    expires_at: datetime
    request_id: RequestId | None = None
