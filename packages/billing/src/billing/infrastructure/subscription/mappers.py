from typing import cast
from uuid import UUID

from billing.domain.shared.ids import UserId
from billing.domain.shared.value_objects import PlanCode
from billing.domain.subscription.entities import (
    Subscription,
)
from billing.domain.subscription.value_objects import (
    SubscriptionId,
    SubscriptionStatus,
)
from billing.infrastructure.subscription.models import (
    SubscriptionModel,
)


def to_domain(model: SubscriptionModel) -> Subscription:
    raw_user_id = model.user_id
    try:
        user_id_value = UUID(raw_user_id)
    except ValueError:
        user_id_value = raw_user_id

    if model.status not in (
        "active",
        "canceled",
        "past_due",
    ):
        raise ValueError(
            f"Invalid subscription status persisted in DB: {model.status}"
        )

    status = cast(SubscriptionStatus, model.status)

    return Subscription(
        subscription_id=SubscriptionId(
            UUID(model.subscription_id)
        ),
        user_id=UserId(user_id_value),
        plan_code=PlanCode(model.plan_code),
        status=status,
        current_period_start=model.current_period_start,
        current_period_end=model.current_period_end,
        cancel_at_period_end=model.cancel_at_period_end,
        provider_subscription_id=model.provider_subscription_id,
    )


def copy_to_model(
    subscription: Subscription,
    model: SubscriptionModel,
) -> SubscriptionModel:
    model.subscription_id = str(
        subscription.subscription_id
    )
    model.user_id = str(subscription.user_id)
    model.plan_code = str(subscription.plan_code)
    model.status = subscription.status
    model.current_period_start = (
        subscription.current_period_start
    )
    model.current_period_end = (
        subscription.current_period_end
    )
    model.cancel_at_period_end = (
        subscription.cancel_at_period_end
    )
    model.provider_subscription_id = (
        subscription.provider_subscription_id
    )
    model.last_granted_period_start = (
        subscription.last_granted_period_start
    )

    return model
