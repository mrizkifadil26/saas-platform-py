from billing.domain.credits.value_objects import Credits
from billing.domain.pricing.entities import SubscriptionPlan
from billing.domain.subscription.entities import (
    Subscription,
)
from billing.domain.subscription.events import (
    SubscriptionCreditGrantRequested,
)


def build_subscription_cycle_key(
    subscription: Subscription,
) -> str:
    return subscription.current_period.cycle_key(
        subscription.subscription_id
    )


def build_subscription_credit_grant_requested(
    *,
    subscription: Subscription,
    plan: SubscriptionPlan,
    request_id=None,
) -> SubscriptionCreditGrantRequested:
    cycle_key = build_subscription_cycle_key(subscription)
    return SubscriptionCreditGrantRequested(
        subscription_id=subscription.subscription_id,
        user_id=subscription.user_id,
        plan_code=subscription.plan_code,
        credits=Credits(int(plan.included_credits)),
        cycle_key=cycle_key,
        period_start=subscription.current_period.starts_at,
        period_end=subscription.current_period.ends_at,
        request_id=request_id,
    )
