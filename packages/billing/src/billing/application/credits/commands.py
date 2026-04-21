from dataclasses import dataclass
from datetime import datetime

from billing.domain.credits.value_objects import Credits
from billing.domain.shared.ids import RequestId, UserId


@dataclass(frozen=True, slots=True)
class ConsumeCreditsCommand:
    user_id: UserId
    cost: Credits
    request_id: RequestId
    metadata: dict[str, str] | None = None
    now: datetime | None = None
