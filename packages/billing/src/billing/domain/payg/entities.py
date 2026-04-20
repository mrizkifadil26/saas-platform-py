from dataclasses import dataclass, field
from datetime import datetime

from billing.domain.credits.value_objects import Credits
from billing.domain.payg.value_objects import PaygPurchaseId
from billing.domain.shared.ids import RequestId, UserId
from billing.domain.shared.value_objects import PlanCode


@dataclass(eq=False, slots=True)
class PaygPurchase:
    purchase_id: PaygPurchaseId
    user_id: UserId
    plan_code: PlanCode
    credits: Credits
    created_at: datetime
    request_id: RequestId | None = None
    metadata: dict[str, str] = field(default_factory=dict)
