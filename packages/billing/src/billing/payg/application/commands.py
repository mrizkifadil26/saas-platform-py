from dataclasses import dataclass
from datetime import datetime

from billing.domain.shared.value_objects import PlanCode
from packages.billing.src.billing.domain.shared.ids import (
    RequestId,
    UserId,
)


@dataclass(frozen=True, slots=True)
class CreatePaygPurchaseCommand:
    user_id: UserId
    plan_code: PlanCode
    request_id: RequestId
    metadata: dict[str, str] | None = None
    now: datetime | None = None
