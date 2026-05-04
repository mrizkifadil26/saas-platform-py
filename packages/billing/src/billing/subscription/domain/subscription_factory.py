from datetime import datetime
from typing import Sequence

from billing.shared.domain.value_objects.user_id import UserId
from billing.subscription.domain.subscription import Subscription
from billing.subscription.domain.subscription_item import SubscriptionItem
from billing.subscription.domain.value_objects.billing_period import BillingPeriod
from billing.subscription.domain.value_objects.plan_code import PlanCode
from billing.subscription.domain.value_objects.subscription_id import SubscriptionId


class SubscriptionFactory:
    @staticmethod
    def create_subscription(
        subscription_id: SubscriptionId,
        user_id: UserId,
        plan_code: PlanCode,
        period_start: datetime,
        period_end: datetime,
        items: Sequence[SubscriptionItem] | None = None,
        provider_subscription_id: str | None = None,
        trial: bool = False,
        occurred_at: datetime | None = None,
    ) -> Subscription:
        return Subscription.create(
            subscription_id=subscription_id,
            user_id=user_id,
            plan_code=plan_code,
            billing_period=BillingPeriod(
                start_at=period_start,
                end_at=period_end,
            ),
            items=list(items or []),
            provider_subscription_id=provider_subscription_id,
            trial=trial,
            occurred_at=occurred_at,
        )
