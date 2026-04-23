from datetime import datetime
from typing import Sequence

from billing.domain.shared.ids import UserId
from billing.domain.subscription.subscription import Subscription
from billing.domain.subscription.subscription_item import SubscriptionItem
from billing.domain.value_objects.billing_period import BillingPeriod
from billing.domain.value_objects.plan_id import PlanId
from billing.domain.value_objects.subscription_id import SubscriptionId


class SubscriptionFactory:
    @staticmethod
    def create_subscription(
        subscription_id: SubscriptionId,
        user_id: UserId,
        plan_id: PlanId,
        period_start: datetime,
        period_end: datetime,
        items: Sequence[SubscriptionItem] | None = None,
        provider_subscription_id: str | None = None,
        trial: bool = False,
    ) -> Subscription:
        return Subscription.create(
            subscription_id=subscription_id,
            user_id=user_id,
            plan_id=plan_id,
            billing_period=BillingPeriod(
                start_at=period_start,
                end_at=period_end,
            ),
            items=list(items or []),
            provider_subscription_id=provider_subscription_id,
            trial=trial,
        )
