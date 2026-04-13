from dataclasses import dataclass, field
from typing import Any, Literal

from billing.domain.types import Credits, PlanCode, RequestId, UserId

BillingEventType = Literal[
    "credits_charged",
    "payg_credits_granted",
    "subscription_credits_granted",
    "subscription_created",
    "subscription_canceled",
    "subscription_renewed",
]


@dataclass(frozen=True)
class BillingEvent:
    event_type: BillingEventType
    user_id: UserId
    credits: Credits = Credits(0)
    request_id: RequestId | None = None
    plan_code: PlanCode | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
