from datetime import timedelta

import pytest

from billing.domain.shared.ids import RequestId, UserId
from billing.domain.shared.value_objects import PlanCode
from billing.domain.subscription.domain_services import (
    cancel_subscription,
    create_subscription,
    grant_subscription_credits,
    renew_subscription,
)
from billing.domain.subscription.entities import (
    Subscription,
)
from billing.domain.subscription.exceptions import (
    DuplicatePeriodGrant,
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


def test_create_subscription_returns_active_subscription_with_requested_plans_and_periods(
    now,
    user_id,
    subscription_id,
):
    next_end = now + timedelta(days=30)

    result = create_subscription(
        subscription_id=subscription_id,
        user_id=user_id,
        plan_code=PlanCode("sub_pro_monthly"),
        current_period_start=now,
        current_period_end=next_end,
        now=now,
    )

    assert result.subscription.subscription_id is not None
    assert result.subscription.user_id == user_id
    assert result.subscription.plan_code == PlanCode(
        "sub_pro_monthly"
    )
    assert result.subscription.status == "active"
    assert result.subscription.current_period_start == now
    assert (
        result.subscription.current_period_end == next_end
    )
    assert result.subscription.cancel_at_period_end is False
    assert (
        result.subscription.last_granted_period_start
        is None
    )


def test_create_subscription_emits_subscription_created_with_period_metadata(
    now,
    user_id,
    subscription_id,
):
    next_end = now + timedelta(days=30)

    result = create_subscription(
        subscription_id=subscription_id,
        user_id=user_id,
        plan_code=PlanCode("sub_pro_monthly"),
        current_period_start=now,
        current_period_end=next_end,
        now=now,
    )

    assert (
        result.event.subscription_id
        == result.subscription.subscription_id
    )
    assert (
        result.event.user_id == result.subscription.user_id
    )
    assert (
        result.event.plan_code
        == result.subscription.plan_code
    )
    assert (
        result.event.metadata["period_start"]
        == now.isoformat()
    )
    assert (
        result.event.metadata["period_end"]
        == next_end.isoformat()
    )


def test_cancel_subscription_immediate_false_sets_cancel_at_period_end_only(
    now,
):
    subscription = make_subscription(
        status="active",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
        cancel_at_period_end=False,
    )

    result = cancel_subscription(
        subscription=subscription,
        immediate=False,
        now=now,
    )

    assert result.subscription.status == "active"
    assert result.subscription.cancel_at_period_end is True


def test_cancel_subscription_immediate_false_emits_event_with_immediate_false(
    now,
):
    subscription = make_subscription(
        status="active",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )

    result = cancel_subscription(
        subscription=subscription,
        immediate=False,
        now=now,
    )

    assert (
        result.event.subscription_id
        == subscription.subscription_id
    )
    assert result.event.immediate is False


def test_cancel_subscription_immediate_true_cancels_immediately_and_emits_matching_event(
    now,
):
    subscription = make_subscription(
        status="active",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )

    result = cancel_subscription(
        subscription=subscription,
        immediate=True,
        now=now,
    )

    assert result.subscription.status == "canceled"
    assert result.subscription.cancel_at_period_end is True
    assert result.event.immediate is True


def test_cancel_subscription_raises_if_subscription_already_canceled(
    now,
):
    subscription = make_subscription(
        status="canceled",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )

    with pytest.raises(InvalidSubscriptionStatus):
        cancel_subscription(
            subscription=subscription,
            immediate=True,
            now=now,
        )


def test_grant_subscription_credits_requires_active_subscription(
    now,
    grant_id,
):
    subscription = make_subscription(
        status="past_due",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )

    with pytest.raises(InvalidSubscriptionStatus):
        grant_subscription_credits(
            grant_id=grant_id,
            subscription=subscription,
            request_id=RequestId("req_123"),
            now=now,
        )


def test_grant_subscription_credits_raises_duplicate_period_grant_if_already_granted(
    now,
    grant_id,
):
    subscription = make_subscription(
        status="active",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
        last_granted_period_start=now,
    )

    with pytest.raises(DuplicatePeriodGrant):
        grant_subscription_credits(
            grant_id=grant_id,
            subscription=subscription,
            request_id=RequestId("req_123"),
            now=now,
        )


def test_grant_subscription_credits_creates_credit_grant_using_plan_credits(
    now,
    grant_id,
):
    subscription = make_subscription(
        status="active",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )

    result = grant_subscription_credits(
        grant_id=grant_id,
        subscription=subscription,
        request_id=RequestId("req_123"),
        now=now,
    )

    plan_credits = result.event.credits

    assert result.grant.granted_credits == plan_credits
    assert result.grant.remaining_credits == plan_credits


def test_grant_subscription_credits_sets_grant_expiry_to_subscription_current_period_end(
    now,
    grant_id,
):
    subscription = make_subscription(
        status="active",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )

    result = grant_subscription_credits(
        grant_id=grant_id,
        subscription=subscription,
        request_id=RequestId("req_123"),
        now=now,
    )

    assert (
        result.grant.expires_at
        == subscription.current_period_end
    )


def test_grant_subscription_credits_sets_grant_source_to_subscription(
    now,
    grant_id,
):
    subscription = make_subscription(
        status="active",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )

    result = grant_subscription_credits(
        grant_id=grant_id,
        subscription=subscription,
        request_id=RequestId("req_123"),
        now=now,
    )

    assert result.grant.source == "subscription"


def test_grant_subscription_credits_updates_last_granted_period_start(
    now,
    grant_id,
):
    subscription = make_subscription(
        status="active",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
        last_granted_period_start=None,
    )

    result = grant_subscription_credits(
        grant_id=grant_id,
        subscription=subscription,
        request_id=RequestId("req_123"),
        now=now,
    )

    assert (
        result.subscription.last_granted_period_start
        == subscription.current_period_start
    )


def test_grant_subscription_credits_emits_event_with_same_credits_plan_and_request_id(
    now,
    grant_id,
):
    subscription = make_subscription(
        status="active",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )

    result = grant_subscription_credits(
        grant_id=grant_id,
        subscription=subscription,
        request_id=RequestId("req_123"),
        now=now,
    )

    assert (
        result.event.subscription_id
        == subscription.subscription_id
    )
    assert result.event.plan_code == subscription.plan_code
    assert result.event.request_id == RequestId("req_123")
    assert (
        result.event.credits == result.grant.granted_credits
    )


def test_renew_subscription_snapshots_previous_subscription_before_mutation(
    now,
):
    subscription = make_subscription(
        status="active",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )
    old_start = subscription.current_period_start
    old_end = subscription.current_period_end
    next_start = now + timedelta(days=30)
    next_end = now + timedelta(days=60)

    result = renew_subscription(
        subscription=subscription,
        next_period_start=next_start,
        next_period_end=next_end,
        now=now,
    )

    assert (
        result.previous_subscription.current_period_start
        == old_start
    )
    assert (
        result.previous_subscription.current_period_end
        == old_end
    )


def test_renew_subscription_mutates_subscription_to_next_period(
    now,
):
    subscription = make_subscription(
        status="past_due",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )
    next_start = now + timedelta(days=30)
    next_end = now + timedelta(days=60)

    result = renew_subscription(
        subscription=subscription,
        next_period_start=next_start,
        next_period_end=next_end,
        now=now,
    )

    assert (
        result.subscription.current_period_start
        == next_start
    )
    assert (
        result.subscription.current_period_end == next_end
    )
    assert result.subscription.status == "active"


def test_renew_subscription_emits_event_with_next_period_metadata(
    now,
):
    subscription = make_subscription(
        status="active",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )
    next_start = now + timedelta(days=30)
    next_end = now + timedelta(days=60)

    result = renew_subscription(
        subscription=subscription,
        next_period_start=next_start,
        next_period_end=next_end,
        now=now,
    )

    assert (
        result.event.subscription_id
        == subscription.subscription_id
    )
    assert (
        result.event.metadata["next_period_start"]
        == next_start.isoformat()
    )
    assert (
        result.event.metadata["next_period_end"]
        == next_end.isoformat()
    )


def test_renew_subscription_raises_if_underlying_entity_cannot_renew(
    now,
):
    subscription = make_subscription(
        status="canceled",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )

    with pytest.raises(InvalidSubscriptionStatus):
        renew_subscription(
            subscription=subscription,
            next_period_start=now + timedelta(days=30),
            next_period_end=now + timedelta(days=60),
            now=now,
        )
