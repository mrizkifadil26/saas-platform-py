from dataclasses import dataclass
from datetime import datetime

from billing.domain.types import PlanCode, SubscriptionId, SubscriptionStatus, UserId


@dataclass(frozen=True)
class Subscription:
    subscription_id: SubscriptionId
    user_id: UserId
    plan_code: PlanCode
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    provider_subscription_id: str | None = None
    last_granted_period_start: datetime | None = None
