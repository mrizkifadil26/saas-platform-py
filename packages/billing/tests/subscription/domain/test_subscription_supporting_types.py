from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from billing.credits.domain.value_objects.credits import Credits
from billing.pricing.domain.entities import SubscriptionPlan
from billing.shared.domain.enums import BillingInterval
from billing.shared.domain.value_objects.currency import Currency
from billing.shared.domain.value_objects.money import Money
from billing.subscription.domain.exceptions import (
    InvalidSubscriptionPeriodError,
    SubscriptionAlreadyCanceledError,
    SubscriptionError,
)
from billing.subscription.domain.plans import CATALOG, PlanCode, get_subscription_plan
from billing.subscription.domain.subscription_events import (
    SubscriptionCanceled,
    SubscriptionChanged,
    SubscriptionRenewed,
    SubscriptionStarted,
)
from billing.subscription.domain.subscription_status import SubscriptionStatus
from billing.subscription.domain.value_objects.billing_period import BillingPeriod
from billing.subscription.domain.value_objects.feature_code import FeatureCode
from billing.subscription.domain.value_objects.plan_id import PlanId
from billing.subscription.domain.value_objects.product_code import ProductCode
from billing.subscription.domain.value_objects.subscription_id import SubscriptionId
from billing.subscription.domain.value_objects.subscription_item_id import (
    SubscriptionItemId,
)


def test_subscription_status_flags():
    assert SubscriptionStatus.ACTIVE.is_activeish is True
    assert SubscriptionStatus.PAST_DUE.can_renew() is True
    assert SubscriptionStatus.CANCELED.is_terminal is True
    assert SubscriptionStatus.PAUSED.is_activeish is False


def test_billing_period_validation_and_helpers(now):
    with pytest.raises(ValueError, match="timezone-aware"):
        BillingPeriod(start_at=now.replace(tzinfo=None), end_at=now)

    with pytest.raises(ValueError, match="after start_at"):
        BillingPeriod(start_at=now, end_at=now)

    period = BillingPeriod(start_at=now, end_at=now + timedelta(days=30))
    adjacent = BillingPeriod(start_at=period.end_at, end_at=period.end_at + timedelta(days=30))
    overlapping = BillingPeriod(start_at=now + timedelta(days=1), end_at=now + timedelta(days=2))

    assert period.contains(now + timedelta(days=1)) is True
    assert period.overlaps(overlapping) is True
    assert period.is_adjacent_to(adjacent) is True
    assert period.next_period(period) == adjacent


@pytest.mark.parametrize(
    ("cls", "value"),
    [
        (PlanId, str(uuid4())),
        (SubscriptionId, str(uuid4())),
        (SubscriptionItemId, str(uuid4())),
        (ProductCode, str(uuid4())),
        (FeatureCode, str(uuid4())),
    ],
)
def test_subscription_ids_wrap_uuid_strings(cls, value):
    wrapped = cls(value)
    assert str(wrapped) == value


def test_subscription_event_types_are_domain_events(subscription_id, user_id, plan_id, now):
    started = SubscriptionStarted(
        subscription_id=subscription_id,
        user_id=user_id,
        plan_id=plan_id,
        occurred_at=now,
    )
    renewed = SubscriptionRenewed(
        subscription_id=subscription_id,
        previous_period_start=now,
        previous_period_end=now + timedelta(days=30),
        new_period_start=now + timedelta(days=30),
        new_period_end=now + timedelta(days=60),
        occurred_at=now,
    )
    changed = SubscriptionChanged(
        subscription_id=subscription_id,
        previous_plan_id=plan_id,
        new_plan_id=PlanId(str(uuid4())),
        occurred_at=now,
    )
    canceled = SubscriptionCanceled(
        subscription_id=subscription_id,
        immediate=True,
        occurred_at=now,
    )

    assert started.event_name == "SubscriptionStarted"
    assert renewed.to_dict()["event_name"] == "SubscriptionRenewed"
    assert changed.subscription_id == subscription_id
    assert canceled.immediate is True


def test_subscription_exceptions_are_subscription_errors():
    assert issubclass(SubscriptionAlreadyCanceledError, SubscriptionError)
    assert issubclass(InvalidSubscriptionPeriodError, SubscriptionError)


def test_get_subscription_plan_returns_catalog_entries():
    plan = get_subscription_plan(PlanCode("sub_basic_monthly"))

    assert isinstance(plan, SubscriptionPlan)
    assert plan.interval == BillingInterval.MONTH
    assert plan.included_credits == Credits(1000)
    assert plan.price == Money(amount=Decimal("99.00"), currency=Currency.USD)
    assert CATALOG[PlanCode("sub_basic_monthly")] == plan


def test_get_subscription_plan_raises_for_unknown_code():
    with pytest.raises(ValueError, match="unknown"):
        get_subscription_plan(PlanCode("unknown"))
