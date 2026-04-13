import pytest
from billing.domain.errors import UnknownPlan
from billing.domain.payg.plans import PaygPlan, get_payg_plan
from billing.domain.types import Credits, PlanCode


def test_get_payg_plan_existing():
    plan = get_payg_plan(PlanCode("payg_10_usd"))
    assert isinstance(plan, PaygPlan)
    assert plan.code == PlanCode("payg_10_usd")
    assert plan.credits_grant == Credits(100)


def test_get_payg_plan_unknown():
    with pytest.raises(UnknownPlan):
        get_payg_plan(PlanCode("unknown"))
