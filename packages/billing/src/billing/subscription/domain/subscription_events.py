from dataclasses import dataclass
from datetime import datetime

from billing.shared.domain.domain_event import DomainEvent
from billing.shared.domain.value_objects.user_id import UserId
from billing.subscription.domain.value_objects.plan_code import PlanCode
from billing.subscription.domain.value_objects.subscription_id import SubscriptionId

# TODO(billing-migration):
# - Replace user_id with customer_id once Customer owns billing identity.
# - Replace plan_code fields with plan_id fields once plans are tenant-scoped and persisted.


@dataclass(frozen=True, slots=True)
class SubscriptionStarted(DomainEvent):
    subscription_id: SubscriptionId
    user_id: UserId
    # TODO: change it with plan_id when we have multi-tenancy
    plan_code: PlanCode


@dataclass(frozen=True, slots=True)
class SubscriptionRenewed(DomainEvent):
    subscription_id: SubscriptionId
    previous_period_start: datetime
    previous_period_end: datetime
    new_period_start: datetime
    new_period_end: datetime


@dataclass(frozen=True, slots=True)
class SubscriptionPlanChanged(DomainEvent):
    subscription_id: SubscriptionId
    previous_plan_code: PlanCode
    new_plan_code: PlanCode


@dataclass(frozen=True, slots=True)
class SubscriptionCanceled(DomainEvent):
    subscription_id: SubscriptionId
    immediate: bool
    effective_at: datetime
