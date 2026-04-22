from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from billing.domain.shared.enums import (
    BillingInterval,
    SubscriptionStatus,
)
from billing.domain.shared.ids import UserId
from billing.domain.shared.value_objects import PlanCode
from billing.domain.subscription.exceptions import (
    InvalidBillingPeriod,
    InvalidSubscriptionStatus,
)
from billing.domain.subscription.value_objects import (
    SubscriptionId,
)


@dataclass(eq=True, slots=True)
class Subscription:
    subscription_id: SubscriptionId
    user_id: UserId
    plan_code: PlanCode

    interval: BillingInterval
    current_period: BillingPeriod
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool

    status: SubscriptionStatus = SubscriptionStatus.PENDING
    provider_subscription_id: str | None = None
    last_granted_period_start: datetime | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None
    _events: list[object] = field(
        default_factory=list, init=False, repr=False
    )

    @property
    def events(self) -> tuple[object, ...]:
        return tuple(self._events)

    def pull_events(self) -> list[object]:
        events = list(self._events)
        self._events.clear()
        return events

    def ensure_active(self) -> None:
        if self.status != "active":
            raise InvalidSubscriptionStatus(
                f"Subscription {self.subscription_id} is not active (status: {self.status})"
            )

    def mark_cancel_at_period_end(self) -> None:
        if self.status == "canceled":
            raise InvalidSubscriptionStatus(
                f"Subscription {self.subscription_id} is already canceled"
            )

        self.cancel_at_period_end = True

    def cancel_immediately(self) -> None:
        if self.status == "canceled":
            raise InvalidSubscriptionStatus(
                f"Subscription {self.subscription_id} is already canceled"
            )

        self.status = SubscriptionStatus.CANCELED
        self.cancel_at_period_end = True

    def can_grant_for_current_period(self) -> bool:
        return (
            self.last_granted_period_start
            != self.current_period_start
        )

    def mark_granted_for_current_period(self) -> None:
        self.last_granted_period_start = (
            self.current_period_start
        )

    def renew(
        self,
        *,
        next_period_start: datetime,
        next_period_end: datetime,
    ) -> None:
        if self.status not in (
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.PAST_DUE,
        ):
            raise InvalidSubscriptionStatus(
                f"Subscription {self.subscription_id} cannot be renewed because it is not active or past due (status: {self.status})"
            )

        self.status = SubscriptionStatus.ACTIVE
        self.current_period_start = next_period_start
        self.current_period_end = next_period_end


@dataclass(frozen=True, slots=True)
class BillingPeriod:
    starts_at: datetime
    ends_at: datetime

    def __post_init__(self) -> None:
        if self.ends_at <= self.starts_at:
            raise InvalidBillingPeriod(
                "billing period end must be after start"
            )

    def contains(self, when: datetime) -> bool:
        return self.starts_at <= when < self.ends_at

    def cycle_key(
        self, subscription_id: SubscriptionId
    ) -> str:
        return f"{subscription_id.value}:{self.starts_at.date().isoformat()}:{self.ends_at.date().isoformat()}"

    def next_period(
        self, interval: BillingInterval
    ) -> BillingPeriod:
        if interval == BillingInterval.MONTH:
            duration = self.ends_at - self.starts_at
            return BillingPeriod(
                starts_at=self.ends_at,
                ends_at=self.ends_at + duration,
            )
        if interval == BillingInterval.YEAR:
            duration = self.ends_at - self.starts_at
            return BillingPeriod(
                starts_at=self.ends_at,
                ends_at=self.ends_at + duration,
            )
        raise SubscriptionStateError(
            f"unsupported interval: {interval}"
        )
