from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from billing.credits.domain.value_objects.credits import Credits
from billing.shared.domain.aggregate_root import AggregateRoot
from billing.shared.domain.value_objects.user_id import UserId
from billing.subscription.domain.exceptions import (
    InvalidSubscriptionStateError,
    SubscriptionAlreadyCanceledError,
)
from billing.subscription.domain.subscription_events import (
    SubscriptionCanceled,
    SubscriptionPlanChanged,
    SubscriptionRenewed,
    SubscriptionStarted,
)
from billing.subscription.domain.subscription_item import SubscriptionItem
from billing.subscription.domain.subscription_status import SubscriptionStatus
from billing.subscription.domain.value_objects.billing_period import BillingPeriod
from billing.subscription.domain.value_objects.plan_code import PlanCode
from billing.subscription.domain.value_objects.subscription_id import SubscriptionId
from billing.subscription.domain.value_objects.subscription_item_id import (
    SubscriptionItemId,
)


@dataclass(slots=True)
class Subscription(AggregateRoot[SubscriptionId]):
    subscription_id: SubscriptionId
    user_id: UserId

    plan_code: PlanCode
    status: SubscriptionStatus
    billing_period: BillingPeriod

    items: tuple[SubscriptionItem, ...] = field(default_factory=tuple)

    cancel_at_period_end: bool = False
    provider_subscription_id: str | None = None
    last_granted_period_start: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if (
            self.last_granted_period_start is not None
            and self.last_granted_period_start.tzinfo is None
        ):
            raise ValueError("last_granted_period_start must be timezone-aware")

        item_ids: set[SubscriptionItemId] = set()
        for item in self.items:
            if item.item_id in item_ids:
                raise ValueError(f"Duplicate SubscriptionItemId: {item.item_id}")

            item_ids.add(item.item_id)

        object.__setattr__(self, "items", tuple(self.items))

    @classmethod
    def create(
        cls,
        *,
        subscription_id: SubscriptionId,
        user_id: UserId,
        plan_code: PlanCode,
        billing_period: BillingPeriod,
        items: list[SubscriptionItem] | None = None,
        provider_subscription_id: str | None = None,
        trial: bool = False,
        metadata: dict[str, Any] | None = None,
        occurred_at: datetime | None = None,
    ) -> Subscription:
        status = SubscriptionStatus.TRIALING if trial else SubscriptionStatus.ACTIVE
        subscription = cls(
            subscription_id=subscription_id,
            user_id=user_id,
            plan_code=plan_code,
            status=status,
            billing_period=billing_period,
            items=tuple(items) if items else tuple(),
            provider_subscription_id=provider_subscription_id,
            metadata=metadata or {},
        )

        event = SubscriptionStarted(
            subscription_id=subscription_id,
            user_id=user_id,
            plan_code=plan_code,
            occurred_at=occurred_at or billing_period.start_at,
        )

        subscription.record_event(event)
        return subscription

    @property
    def current_period_start(self) -> datetime:
        return self.billing_period.start_at

    @property
    def current_period_end(self) -> datetime:
        return self.billing_period.end_at

    def is_active_for_usage(self, at: datetime) -> bool:
        if at.tzinfo is None:
            raise ValueError("at must be timezone-aware")

        if not self.status.is_activeish:
            return False

        return self.billing_period.contains(at)

    def can_be_canceled(self) -> bool:
        return not self.status.is_terminal

    def can_renew(self) -> bool:
        return self.status.can_renew()

    def has_grant_for_current_period(self) -> bool:
        return self.last_granted_period_start == self.current_period_start

    def can_grant_recurring_credits(self) -> bool:
        return (
            self.status == SubscriptionStatus.ACTIVE
            and not self.has_grant_for_current_period()
        )

    def should_end_now(self, at: datetime) -> bool:
        if at.tzinfo is None:
            raise ValueError("at must be timezone-aware")

        if self.status.is_terminal:
            return False

        return self.cancel_at_period_end and at >= self.billing_period.end_at

    def cancel(
        self,
        *,
        immediate: bool = False,
        occurred_at: datetime | None = None,
    ) -> None:
        if self.status == SubscriptionStatus.CANCELED:
            raise SubscriptionAlreadyCanceledError(
                f"Subscription {self.subscription_id} is already canceled"
            )

        if self.status == SubscriptionStatus.EXPIRED:
            raise InvalidSubscriptionStateError(
                f"Cannot cancel subscription {self.subscription_id} because it is expired"
            )

        if immediate:
            self.status = SubscriptionStatus.CANCELED
            self.cancel_at_period_end = False
        else:
            self.cancel_at_period_end = True

        event = SubscriptionCanceled(
            subscription_id=self.subscription_id,
            immediate=immediate,
            effective_at=occurred_at or self.billing_period.start_at,
        )
        self.record_event(event)

    def uncancel(self) -> None:
        if self.status.is_terminal:
            raise InvalidSubscriptionStateError(
                f"Cannot uncancel subscription {self.subscription_id} because it is in terminal status {self.status}"
            )

        self.cancel_at_period_end = False

    def mark_past_due(self) -> None:
        if self.status not in {
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.TRIALING,
        }:
            raise InvalidSubscriptionStateError(
                f"Cannot mark subscription {self.subscription_id} as past due because it is not active or trialing (status: {self.status})"
            )

        self.status = SubscriptionStatus.PAST_DUE

    def pause(self) -> None:
        if self.status not in {
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.PAST_DUE,
            SubscriptionStatus.TRIALING,
        }:
            raise InvalidSubscriptionStateError(
                f"Cannot pause subscription {self.subscription_id} because it is not active or past due (status: {self.status})"
            )

        self.status = SubscriptionStatus.PAUSED

    def resume(self) -> None:
        if self.status != SubscriptionStatus.PAUSED:
            raise InvalidSubscriptionStateError(
                f"Cannot resume subscription {self.subscription_id} because it is not paused (status: {self.status})"
            )

        self.status = SubscriptionStatus.ACTIVE

    def expire(self) -> None:
        if self.status == SubscriptionStatus.EXPIRED:
            return

        self.status = SubscriptionStatus.EXPIRED

    def renew(
        self,
        next_billing_period: BillingPeriod,
        *,
        occurred_at: datetime | None = None,
    ) -> None:
        if not self.can_renew():
            raise InvalidSubscriptionStateError(
                f"Cannot renew subscription {self.subscription_id} "
                f"because it is not in a renewable state (status: {self.status})"
            )

        if self.cancel_at_period_end:
            raise InvalidSubscriptionStateError(
                f"Cannot renew subscription {self.subscription_id} "
                f"because it is set to cancel at period end"
            )

        current_period = self.billing_period

        if not current_period.is_adjacent_to(next_billing_period):
            raise InvalidSubscriptionStateError(
                f"Cannot renew subscription {self.subscription_id} "
                f"because the next billing period {next_billing_period} "
                f"is not adjacent to the current billing period {self.billing_period}"
            )

        if not current_period.is_followed_by(next_billing_period):
            raise InvalidSubscriptionStateError(
                f"Cannot renew subscription {self.subscription_id} "
                f"because the next billing period must start at the current period end"
            )

        self.status = SubscriptionStatus.ACTIVE
        self.billing_period = next_billing_period

        event = SubscriptionRenewed(
            subscription_id=self.subscription_id,
            previous_period_start=current_period.start_at,
            previous_period_end=current_period.end_at,
            new_period_start=next_billing_period.start_at,
            new_period_end=next_billing_period.end_at,
            occurred_at=occurred_at or next_billing_period.start_at,
        )
        self.record_event(event)

    def change_plan(
        self,
        new_plan_code: PlanCode,
        *,
        occurred_at: datetime,
    ) -> None:
        if self.status.is_terminal:
            raise InvalidSubscriptionStateError(
                f"Cannot change plan for subscription {self.subscription_id} "
                f"because it is in terminal status {self.status}"
            )

        # if new_plan_id == self.plan_id:
        if new_plan_code == self.plan_code:
            raise InvalidSubscriptionStateError(
                f"Cannot change to the same plan for subscription {self.subscription_id} "
                f"(plan_code: {self.plan_code})"
            )

        previous_plan_code = self.plan_code
        self.plan_code = new_plan_code

        event = SubscriptionPlanChanged(
            subscription_id=self.subscription_id,
            previous_plan_code=previous_plan_code,
            new_plan_code=new_plan_code,
            occurred_at=occurred_at,
        )
        self.record_event(event)

    def add_item(
        self,
        item: SubscriptionItem,
    ) -> None:
        if any(existing.item_id == item.item_id for existing in self.items):
            raise ValueError(f"Duplicate SubscriptionItemId: {item.item_id}")

        self.items = (*self.items, item)

    def remove_item(
        self,
        item_id: SubscriptionItemId,
    ) -> None:
        remaining_items = tuple(item for item in self.items if item.item_id != item_id)
        if len(remaining_items) == len(self.items):
            raise ValueError(f"SubscriptionItem not found: {item_id}")

        self.items = remaining_items

    def update_item_quantity(
        self,
        item_id: SubscriptionItemId,
        new_quantity: int,
    ) -> None:
        updated = False
        items = []
        for item in self.items:
            if item.item_id == item_id:
                items.append(item.change_quantity(new_quantity))
                updated = True
            else:
                items.append(item)

        if not updated:
            raise ValueError(f"SubscriptionItem not found: {item_id}")

        self.items = tuple(items)

    def mark_credits_granted_for_current_period(
        self,
        credits: Credits,
    ) -> None:
        if credits.is_zero():
            raise ValueError("credits must be greater than zero")

        if self.status != SubscriptionStatus.ACTIVE:
            raise InvalidSubscriptionStateError(
                f"Cannot mark credits as granted for subscription {self.subscription_id} because it is not active"
            )

        if not self.can_grant_recurring_credits():
            raise InvalidSubscriptionStateError(
                f"Cannot mark credits as granted for subscription {self.subscription_id} because it is not active or credits have already been granted for the current period"
            )

        self.last_granted_period_start = self.current_period_start
