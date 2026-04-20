import pytest

from billing.domain.credits.value_objects import Credits
from billing.domain.shared.value_objects import PlanCode
from billing.domain.subscription.exceptions import (
    UnknownPlan,
)
from billing.domain.subscription.plans import (
    CATALOG,
    SubscriptionPlan,
    get_subscription_plan,
)


def test_get_subscription_plan_existing():
    plan = get_subscription_plan(
        PlanCode("sub_basic_monthly")
    )

    assert isinstance(plan, SubscriptionPlan)
    assert plan.code == PlanCode("sub_basic_monthly")
    assert plan.billing_interval == "month"
    assert plan.credits_grant == Credits(1000)
    assert plan.price_cents == 9900
    assert plan.currency == "usd"


def test_get_subscription_plan_returns_expected_pro_plan_fields():
    plan = get_subscription_plan(
        PlanCode("sub_pro_monthly")
    )

    assert plan.code == PlanCode("sub_pro_monthly")
    assert plan.tier == "pro"
    assert plan.billing_interval == "month"
    assert plan.credits_grant == Credits(5000)
    assert plan.price_cents == 29900
    assert plan.currency == "usd"


def test_get_subscription_plan_returns_expected_enterprise_plan_fields():
    plan = get_subscription_plan(
        PlanCode("sub_enterprise_monthly")
    )

    assert plan.code == PlanCode("sub_enterprise_monthly")
    assert plan.tier == "enterprise"
    assert plan.billing_interval == "month"
    assert plan.credits_grant == Credits(20000)
    assert plan.price_cents == 99900
    assert plan.currency == "usd"


def test_get_subscription_plan_unknown():
    with pytest.raises(UnknownPlan, match="unknown"):
        get_subscription_plan(PlanCode("unknown"))


def test_catalog_entries_use_matching_keys_and_codes():
    for key, plan in CATALOG.items():
        assert key == str(plan.code)


def test_catalog_entries_have_positive_price_and_credit_grant():
    for plan in CATALOG.values():
        assert plan.price_cents > 0
        assert int(plan.credits_grant) > 0
