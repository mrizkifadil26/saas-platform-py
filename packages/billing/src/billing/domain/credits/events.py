from dataclasses import dataclass, field
from datetime import datetime

from billing.domain.credits.value_objects import (
    ConsumptionAllocation,
    ConsumptionId,
    Credits,
)
from billing.domain.shared.ids import RequestId, UserId


@dataclass(frozen=True, slots=True)
class CreditsConsumed:
    consumption_id: ConsumptionId
    user_id: UserId
    cost: Credits
    allocations: tuple[ConsumptionAllocation, ...]
    occurred_at: datetime
    request_id: RequestId | None = None
    metadata: dict[str, str] = field(default_factory=dict)
