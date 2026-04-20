from dataclasses import dataclass
from datetime import datetime

from billing.domain.shared.ids import RequestId, UserId
from billing.domain.shared.value_objects import PlanCode
from billing.domain.subscription.value_objects import (
    SubscriptionId,
)


@dataclass(frozen=True, slots=True)
class CreateSubscriptionCommand:
    user_id: UserId
    plan_code: PlanCode
    current_period_start: datetime
    current_period_end: datetime
    provider_subscription_id: str | None = None
    now: datetime | None = None


@dataclass(frozen=True, slots=True)
class CancelSubscriptionCommand:
    subscription_id: SubscriptionId
    immediate: bool = False
    now: datetime | None = None


@dataclass(frozen=True, slots=True)
class GrantSubscriptionCreditsCommand:
    subscription_id: SubscriptionId
    request_id: RequestId | None = None
    now: datetime | None = None


@dataclass(frozen=True, slots=True)
class RenewSubscriptionCommand:
    subscription_id: SubscriptionId
    next_period_start: datetime
    next_period_end: datetime
    now: datetime | None = None
