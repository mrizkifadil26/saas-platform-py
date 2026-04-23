from dataclasses import dataclass
from datetime import datetime

from billing.domain.shared.domain_event import DomainEvent
from billing.domain.shared.ids import UserId
from billing.domain.value_objects.plan_id import PlanId
from billing.domain.value_objects.subscription_id import SubscriptionId


@dataclass(frozen=True, slots=True)
class SubscriptionStarted(DomainEvent):
    subscription_id: SubscriptionId
    # TODO: change it with customer_id when we have multi-tenancy
    user_id: UserId
    plan_id: PlanId
    # TODO: remove old codes after migration
    # plan_code: PlanCode
    # occurred_at: datetime
    # metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SubscriptionRenewed(DomainEvent):
    subscription_id: SubscriptionId
    previous_period_start: datetime
    previous_period_end: datetime
    new_period_start: datetime
    new_period_end: datetime
    # TODO: remove old codes after migration
    # user_id: UserId
    # plan_code: PlanCode
    # occurred_at: datetime
    # metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SubscriptionChanged(DomainEvent):
    subscription_id: SubscriptionId
    previous_plan_id: PlanId
    new_plan_id: PlanId
    # TODO: remove old codes after migration
    # occurred_at: datetime


@dataclass(frozen=True, slots=True)
class SubscriptionCanceled(DomainEvent):
    subscription_id: SubscriptionId
    immediate: bool
    # TODO: remove old codes after migration
    # user_id: UserId
    # plan_code: PlanCode
    # occurred_at: datetime
    # metadata: dict[str, str] = field(default_factory=dict)


# @dataclass(frozen=True, slots=True)
# class SubscriptionCreditsGranted:
#     subscription_id: SubscriptionId
#     user_id: UserId
#     plan_code: PlanCode
#     credits: Credits
#     occurred_at: datetime
#     request_id: RequestId | None = None
#     metadata: dict[str, str] = field(default_factory=dict)


# @dataclass(frozen=True, slots=True)
# class SubscriptionCreditGrantRequested(DomainEvent):
#     subscription_id: SubscriptionId
#     user_id: UserId
#     plan_code: PlanCode
#     credits: Credits
#     cycle_key: str
#     period_start: datetime
#     period_end: datetime
#     request_id: RequestId | None = None
