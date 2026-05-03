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
    # TODO: should use customer_id instead of user_id
    user_id: str
    # TODO: should use plan_id instead of plan_code later
    # plan_id: str
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
    # TODO: should use plan_id instead of plan_code later
    # new_plan_id: str
    new_plan_code: str
    # request_id: RequestId | None = None

@dataclass(frozen=True, slots=True)
class CancelSubscriptionCommand:
    subscription_id: str
    immediate: bool = False
