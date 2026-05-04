from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class CreateSubscriptionItemCommand:
    item_id: str
    product_code: str
    feature_code: str
    quantity: int = 1


@dataclass(frozen=True, slots=True)
class CreateSubscriptionCommand:
    user_id: str
    plan_code: str
    period_start: datetime
    period_end: datetime
    items: tuple[CreateSubscriptionItemCommand, ...] = ()
    provider_subscription_id: str | None = None
    trial: bool = False


@dataclass(frozen=True, slots=True)
class RenewSubscriptionCommand:
    subscription_id: str
    next_period_start: datetime
    next_period_end: datetime


@dataclass(frozen=True, slots=True)
class ChangeSubscriptionPlanCommand:
    subscription_id: str
    new_plan_code: str


@dataclass(frozen=True, slots=True)
class CancelSubscriptionCommand:
    subscription_id: str
    immediate: bool = False
