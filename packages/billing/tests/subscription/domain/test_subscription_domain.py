from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

import pytest

from billing.credits.domain.value_objects.credits import Credits
from billing.subscription.domain.exceptions import (
    InvalidSubscriptionStateError,
    SubscriptionAlreadyCanceledError,
)
from billing.subscription.domain.subscription import Subscription
from billing.subscription.domain.subscription_events import (
    SubscriptionCanceled,
    SubscriptionChanged,
    SubscriptionRenewed,
    SubscriptionStarted,
)
from billing.subscription.domain.subscription_factory import SubscriptionFactory
from billing.subscription.domain.subscription_status import SubscriptionStatus
from billing.subscription.domain.value_objects.billing_period import BillingPeriod
from billing.subscription.domain.value_objects.plan_id import PlanId
from billing.subscription.domain.value_objects.subscription_item_id import (
    SubscriptionItemId,
)


def test_create_records_subscription_started_event(
    user_id,
    plan_id,
    subscription_id,
    billing_period,
):
    subscription = Subscription.create(
        subscription_id=subscription_id,
        user_id=user_id,
        plan_id=plan_id,
        billing_period=billing_period,
        occurred_at=billing_period.start_at,
    )

    events = subscription.domain_events

    assert subscription.status == SubscriptionStatus.ACTIVE
    assert len(events) == 1
    assert isinstance(events[0], SubscriptionStarted)
    assert events[0].subscription_id == subscription_id


def test_create_uses_trial_status_when_requested(
    user_id,
    plan_id,
    subscription_id,
    billing_period,
):
    subscription = Subscription.create(
        subscription_id=subscription_id,
        user_id=user_id,
        plan_id=plan_id,
        billing_period=billing_period,
        trial=True,
    )

    assert subscription.status == SubscriptionStatus.TRIALING


def test_factory_creates_subscription_with_requested_period(
    user_id,
    plan_id,
    subscription_id,
    billing_period,
    subscription_item,
):
    subscription = SubscriptionFactory.create_subscription(
        subscription_id=subscription_id,
        user_id=user_id,
        plan_id=plan_id,
        period_start=billing_period.start_at,
        period_end=billing_period.end_at,
        items=(subscription_item,),
        occurred_at=billing_period.start_at,
    )

    assert subscription.subscription_id == subscription_id
    assert subscription.billing_period == billing_period
    assert subscription.items == (subscription_item,)


def test_duplicate_item_ids_are_rejected(make_subscription, subscription_item):
    duplicate = subscription_item.change_quantity(3)

    with pytest.raises(ValueError, match="Duplicate SubscriptionItemId"):
        make_subscription(items=(subscription_item, duplicate))


def test_is_active_for_usage_requires_timezone_aware_datetime(subscription, now):
    with pytest.raises(ValueError, match="timezone-aware"):
        subscription.is_active_for_usage(now.replace(tzinfo=None))


def test_is_active_for_usage_checks_status_and_period(make_subscription, billing_period):
    active = make_subscription(status=SubscriptionStatus.ACTIVE)
    canceled = make_subscription(status=SubscriptionStatus.CANCELED)
    after_period = billing_period.end_at + timedelta(seconds=1)

    assert active.is_active_for_usage(billing_period.start_at) is True
    assert active.is_active_for_usage(after_period) is False
    assert canceled.is_active_for_usage(billing_period.start_at) is False


def test_cancel_at_period_end_records_non_immediate_event(subscription, now):
    updated = subscription.cancel(immediate=False, occurred_at=now)
    event = updated.domain_events[0]

    assert updated.status == SubscriptionStatus.ACTIVE
    assert updated.cancel_at_period_end is True
    assert isinstance(event, SubscriptionCanceled)
    assert event.immediate is False


def test_cancel_immediately_sets_canceled_state(subscription, now):
    updated = subscription.cancel(immediate=True, occurred_at=now)

    assert updated.status == SubscriptionStatus.CANCELED
    assert updated.cancel_at_period_end is False
    assert isinstance(updated.domain_events[0], SubscriptionCanceled)


def test_cancel_rejects_terminal_states(make_subscription, now):
    canceled = make_subscription(status=SubscriptionStatus.CANCELED)
    expired = make_subscription(status=SubscriptionStatus.EXPIRED)

    with pytest.raises(SubscriptionAlreadyCanceledError):
        canceled.cancel(immediate=True, occurred_at=now)

    with pytest.raises(InvalidSubscriptionStateError):
        expired.cancel(immediate=True, occurred_at=now)


def test_uncancel_reopens_non_terminal_subscription(make_subscription):
    subscription = make_subscription(cancel_at_period_end=True)

    updated = subscription.uncancel()

    assert updated.cancel_at_period_end is False


def test_mark_past_due_pause_resume_and_expire_transitions(subscription):
    past_due = subscription.mark_past_due()
    paused = past_due.pause()
    resumed = paused.resume()
    expired = resumed.expire()

    assert past_due.status == SubscriptionStatus.PAST_DUE
    assert paused.status == SubscriptionStatus.PAUSED
    assert resumed.status == SubscriptionStatus.ACTIVE
    assert expired.status == SubscriptionStatus.EXPIRED


def test_renew_updates_period_and_records_event(
    subscription,
    next_billing_period,
    now,
):
    updated = subscription.renew(
        next_billing_period=next_billing_period,
        occurred_at=now,
    )
    event = updated.domain_events[0]

    assert updated.billing_period == next_billing_period
    assert updated.status == SubscriptionStatus.ACTIVE
    assert isinstance(event, SubscriptionRenewed)
    assert event.previous_period_start == subscription.current_period_start
    assert event.new_period_end == next_billing_period.end_at


def test_renew_rejects_invalid_state_or_overlapping_period(
    make_subscription,
    billing_period,
    next_billing_period,
):
    canceled = make_subscription(status=SubscriptionStatus.CANCELED)
    canceling = make_subscription(cancel_at_period_end=True)
    overlapping = BillingPeriod(
        start_at=billing_period.start_at + timedelta(days=1),
        end_at=billing_period.end_at + timedelta(days=31),
    )

    with pytest.raises(InvalidSubscriptionStateError):
        canceled.renew(next_billing_period)

    with pytest.raises(InvalidSubscriptionStateError):
        canceling.renew(next_billing_period)

    with pytest.raises(InvalidSubscriptionStateError):
        make_subscription().renew(overlapping)


def test_change_plan_updates_plan_and_records_event(subscription, new_plan_id, now):
    updated = subscription.change_plan(new_plan_id=new_plan_id, occurred_at=now)
    event = updated.domain_events[0]

    assert updated.plan_id == new_plan_id
    assert isinstance(event, SubscriptionChanged)
    assert event.previous_plan_id == subscription.plan_id


def test_change_plan_rejects_terminal_and_same_plan(make_subscription, plan_id, now):
    expired = make_subscription(status=SubscriptionStatus.EXPIRED)

    with pytest.raises(InvalidSubscriptionStateError):
        expired.change_plan(new_plan_id=PlanId(str(uuid4())), occurred_at=now)

    with pytest.raises(InvalidSubscriptionStateError):
        make_subscription().change_plan(new_plan_id=plan_id, occurred_at=now)


def test_item_operations_add_remove_and_update_quantity(subscription):
    new_item_id = SubscriptionItemId(str(uuid4()))
    added = subscription.add_item(
        subscription.items[0].__class__(
            item_id=new_item_id,
            product_code=subscription.items[0].product_code,
            feature_code=subscription.items[0].feature_code,
            quantity=5,
        )
    )
    updated = added.update_item_quantity(new_item_id, 7)
    removed = updated.remove_item(new_item_id)

    assert len(added.items) == 2
    assert [item.quantity for item in updated.items if item.item_id == new_item_id] == [7]
    assert removed.items == subscription.items


def test_mark_credits_granted_for_current_period_updates_grant_marker(subscription):
    updated = subscription.mark_credits_granted_for_current_period(Credits(10))

    assert updated.last_granted_period_start == subscription.current_period_start
    assert updated.can_grant_recurring_credits() is False


def test_mark_credits_granted_for_current_period_rejects_zero_or_ineligible(
    make_subscription,
):
    base = make_subscription()
    inactive = make_subscription(status=SubscriptionStatus.PAST_DUE)
    already_granted = make_subscription(
        last_granted_period_start=base.current_period_start,
    )

    with pytest.raises(ValueError):
        base.mark_credits_granted_for_current_period(Credits.zero())

    with pytest.raises(InvalidSubscriptionStateError):
        inactive.mark_credits_granted_for_current_period(Credits(1))

    with pytest.raises(InvalidSubscriptionStateError):
        already_granted.mark_credits_granted_for_current_period(Credits(1))


def test_should_end_now_checks_cancel_flag_and_period_end(subscription, billing_period):
    canceling = subscription.cancel(immediate=False)

    assert canceling.should_end_now(billing_period.end_at) is True
    assert canceling.should_end_now(billing_period.start_at) is False
    assert subscription.should_end_now(billing_period.end_at) is False
