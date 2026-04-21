from dataclasses import dataclass
from datetime import datetime

from packages.billing.src.billing.domain.shared.ids import (
    RequestId,
    UserId,
)

from billing.domain.shared.value_objects import PlanCode


@dataclass(frozen=True, slots=True)
class CreatePaygPurchaseCommand:
    user_id: UserId
    plan_code: PlanCode
    request_id: RequestId
    metadata: dict[str, str] | None = None
    now: datetime | None = None
