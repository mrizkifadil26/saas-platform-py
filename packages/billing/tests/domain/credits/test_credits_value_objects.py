# packages/billing/tests/domain/credits/test_value_objects.py

import pytest
from billing.domain.credits.exceptions import (
    InvalidCreditsAmount,
)
from billing.domain.credits.value_objects import (
    ConsumptionAllocation,
    ConsumptionId,
    Credits,
    GrantId,
)


def test_credits_accepts_zero():
    value = Credits(0)

    assert int(value) == 0


def test_credits_accepts_positive_values():
    value = Credits(100)

    assert int(value) == 100


def test_credits_rejects_negative_values():
    with pytest.raises(InvalidCreditsAmount):
        Credits(-1)


def test_credits_int_returns_raw_integer():
    value = Credits(42)

    assert int(value) == 42


def test_credits_is_zero_returns_true_only_for_zero():
    assert Credits(0).is_zero() is True
    assert Credits(1).is_zero() is False


def test_credits_add_returns_summed_credits():
    result = Credits(40) + Credits(2)

    assert result == Credits(42)


def test_credits_sub_returns_remaining_credits_when_sufficient():
    result = Credits(100) - Credits(40)

    assert result == Credits(60)


def test_credits_sub_raises_on_underflow():
    with pytest.raises(InvalidCreditsAmount):
        Credits(10) - Credits(11)


def test_credits_str_returns_numeric_string():
    value = Credits(42)

    assert str(value) == "42"


def test_grant_id_new_returns_uuid_backed_id():
    value = GrantId.new()

    assert isinstance(value, GrantId)
    assert str(value)
    assert len(str(value)) == 36


def test_consumption_id_new_returns_uuid_backed_id():
    value = ConsumptionId.new()

    assert isinstance(value, ConsumptionId)
    assert str(value)
    assert len(str(value)) == 36


def test_consumption_allocation_stores_grant_id_and_credits_unchanged():
    grant_id = GrantId.new()
    allocation = ConsumptionAllocation(
        grant_id=grant_id,
        credits=Credits(25),
    )

    assert allocation.grant_id == grant_id
    assert allocation.credits == Credits(25)
