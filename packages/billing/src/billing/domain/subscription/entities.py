from dataclasses import dataclass
from datetime import datetime

from packages.billing.src.billing.domain.shared.value_objects import (
    PlanCode,
)

from billing.domain.shared.ids import UserId
from billing.domain.subscription.exceptions import (
    InvalidSubscriptionStatus,
)
from billing.domain.subscription.value_objects import (
    SubscriptionId,
    SubscriptionStatus,
)


@dataclass(eq=True, slots=True)
class Subscription:
    subscription_id: SubscriptionId
    user_id: UserId
    plan_code: PlanCode
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    provider_subscription_id: str | None = None
    last_granted_period_start: datetime | None = None

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

        self.status = "canceled"
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
        if self.status not in ("active", "past_due"):
            raise InvalidSubscriptionStatus(
                f"Subscription {self.subscription_id} cannot be renewed because it is not active or past due (status: {self.status})"
            )

        self.status = "active"
        self.current_period_start = next_period_start
        self.current_period_end = next_period_end
