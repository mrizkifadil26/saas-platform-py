from dataclasses import dataclass, field
from datetime import datetime

from packages.billing.src.billing.domain.credits.value_objects import (
    Credits,
)
from packages.billing.src.billing.domain.shared.ids import (
    RequestId,
    UserId,
)
from packages.billing.src.billing.domain.shared.value_objects import (
    PlanCode,
)


@dataclass(frozen=True, slots=True)
class PaygCreditsGranted:
    user_id: UserId
    plan_code: PlanCode
    credits: Credits
    occurred_at: datetime
    request_id: RequestId | None = None
    metadata: dict[str, str] | None = field(default=None)
