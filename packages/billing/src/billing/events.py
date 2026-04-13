from dataclasses import dataclass, field
from typing import Any, Literal

from billing.types import Credits, PlanCode, RequestId, UserId

BillingEventType = Literal[
    "credits_charged",
    "payg_credits_granted",
    "subscription_credits_granted",
]


@dataclass(frozen=True)
class BillingEvent:
    event_type: BillingEventType
    user_id: UserId
    credits: Credits
    request_id: RequestId | None = None
    plan_code: PlanCode | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
