from dataclasses import dataclass, field
from datetime import datetime

from billing.domain.credits.value_objects import Credits
from billing.domain.shared.ids import RequestId, UserId
from billing.domain.shared.value_objects import PlanCode


@dataclass(frozen=True, slots=True)
class PaygCreditsPurchased:
    purchase_id: str
    user_id: UserId
    plan_code: PlanCode
    credits: Credits
    occurred_at: datetime
    request_id: RequestId | None = None
    metadata: dict[str, str] = field(default_factory=dict)
