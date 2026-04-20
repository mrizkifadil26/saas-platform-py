from datetime import timedelta

import pytest

from billing.domain.shared.ids import UserId
from billing.domain.shared.value_objects import PlanCode
from billing.domain.subscription.entities import (
    Subscription,
)
from billing.domain.subscription.exceptions import (
    InvalidSubscriptionStatus,
)
from billing.domain.subscription.value_objects import (
    SubscriptionId,
    SubscriptionStatus,
)


def make_subscription(
    *,
    status: SubscriptionStatus = "active",
    current_period_start,
    current_period_end,
    cancel_at_period_end: bool = False,
    last_granted_period_start=None,
):
    return Subscription(
        subscription_id=SubscriptionId.new(),
        user_id=UserId("user_123"),
        plan_code=PlanCode("sub_pro_monthly"),
        status=status,
        current_period_start=current_period_start,
        current_period_end=current_period_end,
        cancel_at_period_end=cancel_at_period_end,
        last_granted_period_start=last_granted_period_start,
    )


def test_subscription_ensure_active_passes_for_active(now):
    subscription = make_subscription(
        status="active",
        current_period_start=now,
        current_period_end=now,
    )

    subscription.ensure_active()  # Should not raise


def test_subscription_ensure_active_raises_for_past_due(
    now,
):
    subscription = make_subscription(
        status="past_due",
        current_period_start=now,
        current_period_end=now,
    )

    with pytest.raises(InvalidSubscriptionStatus):
        subscription.ensure_active()


def test_subscription_ensure_active_raises_for_canceled(
    now,
):
    subscription = make_subscription(
        status="canceled",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
        cancel_at_period_end=False,
    )

    # subscription.mark_cancel_at_period_end()
    # assert subscription.cancel_at_period_end is True
    with pytest.raises(InvalidSubscriptionStatus):
        subscription.ensure_active()


def test_mark_cancel_at_period_end_raises_when_already_canceled(
    now,
):
    subscription = make_subscription(
        status="canceled",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )

    with pytest.raises(InvalidSubscriptionStatus):
        subscription.mark_cancel_at_period_end()


def test_cancel_immediately_raises_when_already_canceled(
    now,
):
    subscription = make_subscription(
        status="canceled",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )

    with pytest.raises(InvalidSubscriptionStatus):
        subscription.cancel_immediately()


def test_can_grant_for_current_period_true_when_last_granted_period_start_differs(
    now,
):
    subscription = make_subscription(
        status="active",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
        last_granted_period_start=now - timedelta(days=30),
    )

    assert (
        subscription.can_grant_for_current_period() is True
    )


def test_can_grant_for_current_period_false_when_already_granted_for_current_period(
    now,
):
    subscription = make_subscription(
        status="active",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
        last_granted_period_start=now,
    )

    assert (
        subscription.can_grant_for_current_period() is False
    )


def test_mark_granted_for_current_period_updates_last_granted_period_start(
    now,
):
    subscription = make_subscription(
        status="active",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
        last_granted_period_start=None,
    )

    subscription.mark_granted_for_current_period()

    assert (
        subscription.last_granted_period_start
        == subscription.current_period_start
    )


def test_renew_accepts_active_and_updates_period_bounds(
    now,
):
    subscription = make_subscription(
        status="active",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )
    next_start = now + timedelta(days=30)
    next_end = now + timedelta(days=60)

    subscription.renew(
        next_period_start=next_start,
        next_period_end=next_end,
    )

    assert subscription.status == "active"
    assert subscription.current_period_start == next_start
    assert subscription.current_period_end == next_end


def test_renew_accepts_past_due_and_resets_status_to_active(
    now,
):
    subscription = make_subscription(
        status="past_due",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )
    next_start = now + timedelta(days=30)
    next_end = now + timedelta(days=60)

    subscription.renew(
        next_period_start=next_start,
        next_period_end=next_end,
    )

    assert subscription.status == "active"
    assert subscription.current_period_start == next_start
    assert subscription.current_period_end == next_end


def test_renew_raises_for_canceled(now):
    subscription = make_subscription(
        status="canceled",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )

    with pytest.raises(InvalidSubscriptionStatus):
        subscription.renew(
            next_period_start=now + timedelta(days=30),
            next_period_end=now + timedelta(days=60),
        )
