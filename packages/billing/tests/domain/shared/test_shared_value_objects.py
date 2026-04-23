# packages/billing/tests/domain/shared/test_value_objects.py

import pytest
from billing.domain.shared.value_objects import PlanCode


def test_plan_code_trims_surrounding_whitespace():
    value = PlanCode("  sub_pro_monthly  ")

    assert value.value == "sub_pro_monthly"


def test_plan_code_rejects_empty_string():
    with pytest.raises(ValueError, match="PlanCode"):
        PlanCode("   ")


def test_plan_code_str_returns_normalized_value():
    value = PlanCode("  sub_pro_monthly  ")

    assert str(value) == "sub_pro_monthly"
