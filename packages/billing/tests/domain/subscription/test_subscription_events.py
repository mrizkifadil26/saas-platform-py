from datetime import timedelta

from billing.domain.credits.value_objects import Credits
from billing.domain.shared.ids import UserId
from billing.domain.shared.value_objects import PlanCode
from billing.domain.subscription.events import (
    SubscriptionCanceled,
    SubscriptionCreated,
    SubscriptionCreditsGranted,
    SubscriptionRenewed,
)


def test_subscription_created_smoke(
    now,
    subscription_id,
    user_id,
):
    event = SubscriptionCreated(
        subscription_id=subscription_id,
        user_id=user_id,
        plan_code=PlanCode("sub_pro_monthly"),
        occurred_at=now,
        metadata={},
    )

    assert event.subscription_id
    assert event.user_id == UserId("user_123")
    assert event.plan_code == PlanCode("sub_pro_monthly")
    assert event.metadata == {}


def test_subscription_canceled_smoke(
    now,
    subscription_id,
    user_id,
):
    event = SubscriptionCanceled(
        subscription_id=subscription_id,
        user_id=user_id,
        plan_code=PlanCode("sub_pro_monthly"),
        immediate=True,
        occurred_at=now,
        metadata={},
    )

    assert event.subscription_id
    assert event.user_id == UserId("user_123")
    assert event.immediate is True
    assert event.metadata == {}


def test_subscription_credits_granted_smoke(
    now,
    subscription_id,
    user_id,
    request_id,
):
    event = SubscriptionCreditsGranted(
        subscription_id=subscription_id,
        user_id=user_id,
        plan_code=PlanCode("sub_pro_monthly"),
        request_id=request_id,
        credits=Credits(100),
        occurred_at=now,
        metadata={},
    )

    assert event.subscription_id
    assert event.user_id == UserId("user_123")
    assert event.plan_code == PlanCode("sub_pro_monthly")
    assert event.request_id == request_id
    assert event.credits == Credits(100)
    assert event.metadata == {}


def test_subscription_renewed_smoke(
    now,
    subscription_id,
    user_id,
):
    event = SubscriptionRenewed(
        subscription_id=subscription_id,
        user_id=user_id,
        plan_code=PlanCode("sub_pro_monthly"),
        occurred_at=now,
        metadata={
            "next_period_start": now,
            "next_period_end": now + timedelta(days=30),
        },
    )

    assert event.subscription_id
    assert event.user_id == UserId("user_123")
    assert event.metadata["next_period_start"] == now
    assert event.metadata[
        "next_period_end"
    ] == now + timedelta(days=30)
