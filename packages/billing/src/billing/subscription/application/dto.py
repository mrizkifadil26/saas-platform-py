from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class SubscriptionItemDTO:
    item_id: str
    product_code: str
    feature_code: str
    quantity: int


@dataclass(frozen=True, slots=True)
class SubscriptionDTO:
    subscription_id: str
    # TODO: should use customer_id instead of user_id
    user_id: str
    # TODO: later we should use plan_id instead of plan_code, but for now we need to keep plan_code for backward compatibility with existing subscriptions
    # plan_id=str(subscription.plan_id),
    plan_code: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    provider_subscription_id: str | None
    items: tuple[SubscriptionItemDTO, ...] = ()
    # TODO: still confused about this field, should we put it here?
    # last_granted_period_start: datetime | None
