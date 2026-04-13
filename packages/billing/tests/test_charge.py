import pytest

from billing import (
    Credits,
    IdempotencyConflict,
    InsufficientCredits,
    RequestId,
    charge_credits,
)


def test_charge_successful():
    result = charge_credits(Credits(100), Credits(50))
    assert result == Credits(50)


def test_charge_insufficient_credits():
    with pytest.raises(InsufficientCredits):
        charge_credits(Credits(10), Credits(50))


def test_charge_with_idempotency_success():
    used_ids = set()
    result = charge_credits(Credits(100), Credits(50), RequestId("req1"), used_ids)
    assert result == Credits(50)
    assert "req1" in used_ids


def test_charge_with_idempotency_conflict():
    used_ids = {"req1"}
    with pytest.raises(IdempotencyConflict):
        charge_credits(Credits(100), Credits(50), RequestId("req1"), used_ids)
