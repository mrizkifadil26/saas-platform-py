from dataclasses import dataclass, field
from datetime import datetime

from packages.billing.src.billing.domain.credits.value_objects import (
    Credits,
)
from packages.billing.src.billing.domain.payg.value_objects import (
    PaygPurchaseId,
)
from packages.billing.src.billing.domain.shared.ids import (
    RequestId,
    UserId,
)
from packages.billing.src.billing.domain.shared.value_objects import (
    PlanCode,
)


@dataclass(eq=False, slots=True)
class PaygPurchase:
    purchase_id: PaygPurchaseId
    user_id: UserId
    plan_code: PlanCode
    credits: Credits
    created_at: datetime
    request_id: RequestId | None = None
    metadata: dict[str, str] = field(default_factory=dict)
