from dataclasses import dataclass
from datetime import datetime

from billing.shared.domain.domain_event import DomainEvent
from billing.shared.domain.value_objects.user_id import UserId
from billing.subscription.domain.value_objects.plan_code import PlanCode
from billing.subscription.domain.value_objects.subscription_id import SubscriptionId


@dataclass(frozen=True, slots=True)
class SubscriptionStarted(DomainEvent):
    subscription_id: SubscriptionId
    # TODO: change it with customer_id when we have multi-tenancy
    user_id: UserId
    # TODO: change it with plan_id when we have multi-tenancy
    # plan_id: PlanId
    plan_code: PlanCode
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
    # metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SubscriptionPlanChanged(DomainEvent):
    subscription_id: SubscriptionId
    # TODO: plan_id should be used instead of plan_code after we have multi-tenancy
    # previous_plan_id: PlanId
    # new_plan_id: PlanId
    previous_plan_code: PlanCode
    new_plan_code: PlanCode


@dataclass(frozen=True, slots=True)
class SubscriptionCanceled(DomainEvent):
    subscription_id: SubscriptionId
    immediate: bool
    effective_at: datetime
