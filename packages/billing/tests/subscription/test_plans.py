import pytest
from billing.core.errors import UnknownPlan
from billing.core.subscription.plans import SubscriptionPlan, get_subscription_plan
from billing.core.types import Credits, PlanCode


def test_get_subscription_plan_existing():
    plan = get_subscription_plan(PlanCode("sub_basic_monthly"))
    assert isinstance(plan, SubscriptionPlan)
    assert plan.code == PlanCode("sub_basic_monthly")
    assert plan.billing_interval == "month"
    assert plan.credits_grant == Credits(1000)
    assert plan.price_cents == 9900
    assert plan.currency == "usd"


def test_get_subscription_plan_unknown():
    with pytest.raises(UnknownPlan):
        get_subscription_plan(PlanCode("unknown"))
