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
    user_id: str
    plan_code: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    provider_subscription_id: str | None
    items: tuple[SubscriptionItemDTO, ...] = ()
