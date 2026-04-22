from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from billing.domain.credits.value_objects import Credits
from billing.domain.shared.domain_event import DomainEvent
from billing.domain.shared.ids import RequestId, UserId
from billing.domain.shared.value_objects import PlanCode
from billing.domain.subscription.value_objects import (
    SubscriptionId,
)


@dataclass(frozen=True, slots=True)
class SubscriptionCreated:
    subscription_id: SubscriptionId
    user_id: UserId
    plan_code: PlanCode
    occurred_at: datetime
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SubscriptionCanceled:
    subscription_id: SubscriptionId
    user_id: UserId
    plan_code: PlanCode
    occurred_at: datetime
    immediate: bool
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SubscriptionCreditsGranted:
    subscription_id: SubscriptionId
    user_id: UserId
    plan_code: PlanCode
    credits: Credits
    occurred_at: datetime
    request_id: RequestId | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SubscriptionRenewed:
    subscription_id: SubscriptionId
    user_id: UserId
    plan_code: PlanCode
    occurred_at: datetime
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SubscriptionCreditGrantRequested(DomainEvent):
    subscription_id: SubscriptionId
    user_id: UserId
    plan_code: PlanCode
    credits: Credits
    cycle_key: str
    period_start: datetime
    period_end: datetime
    request_id: RequestId | None = None
