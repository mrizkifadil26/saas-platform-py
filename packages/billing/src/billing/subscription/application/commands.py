from dataclasses import dataclass
from datetime import datetime

from billing.shared.domain.value_objects.request_id import RequestId
from billing.shared.domain.value_objects.user_id import UserId
from billing.subscription.domain.plans import PlanCode
from billing.subscription.domain.value_objects.subscription_id import SubscriptionId


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
