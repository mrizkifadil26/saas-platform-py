from dataclasses import dataclass

from billing.domain.payg.value_objects import (
    PackCode,
    PaygPurchaseId,
)
from billing.domain.shared.events import DomainEvent
from billing.domain.shared.ids import UserId

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
class PaygPurchasePaid(DomainEvent):
    purchase_id: PaygPurchaseId
    user_id: UserId
    pack_code: PackCode
