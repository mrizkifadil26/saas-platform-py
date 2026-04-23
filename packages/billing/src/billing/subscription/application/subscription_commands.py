from dataclasses import dataclass
from datetime import datetime

from billing.shared.domain.value_objects.request_id import RequestId
from billing.shared.domain.value_objects.user_id import UserId
from billing.subscription.domain.plans import PlanCode
from billing.subscription.domain.value_objects.subscription_id import SubscriptionId


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
    plan_id: str
    current_period_start: datetime
    current_period_end: datetime
    items: tuple[CreateSubscriptionItemCommand, ...] = ()
    provider_subscription_id: str | None = None
    trial: bool = False
    # now: datetime | None = None


@dataclass(frozen=True, slots=True)
class RenewSubscriptionCommand:
    subscription_id: str
    next_period_start: datetime
    next_period_end: datetime
    # now: datetime | None = None


@dataclass(frozen=True, slots=True)
class ChangeSubscriptionPlanCommand:
    subscription_id: str
    new_plan_id: str
    # request_id: RequestId | None = None
    # now: datetime | None = None


@dataclass(frozen=True, slots=True)
class CancelSubscriptionCommand:
    subscription_id: str
    immediate: bool = False
    # now: datetime | None = None


# @dataclass(frozen=True, slots=True)
# class GrantSubscriptionCreditsCommand:
#     subscription_id: SubscriptionId
#     request_id: RequestId | None = None
#     now: datetime | None = None
