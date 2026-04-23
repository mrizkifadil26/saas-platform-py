# packages/billing/tests/domain/credits/test_entities.py

from datetime import timedelta

import pytest
from billing.domain.credits.entities import (
    CreditConsumption,
    CreditGrant,
)
from billing.domain.credits.exceptions import (
    InvalidCreditsAmount,
)
from billing.domain.credits.value_objects import (
    ConsumptionAllocation,
    Credits,
    GrantId,
)
from billing.domain.shared.enums import CreditSource
from billing.domain.shared.ids import UserId


def make_credit_grant(
    *,
    now,
    user_id: UserId | None = None,
    granted_credits: Credits = Credits(100),
    remaining_credits: Credits = Credits(100),
    source: CreditSource = "subscription",
    expires_at=None,
    metadata: dict | None = None,
):
    return CreditGrant(
        grant_id=GrantId.new(),
        user_id=user_id or UserId("user_123"),
        granted_credits=granted_credits,
        remaining_credits=remaining_credits,
        source=source,
        created_at=now,
        expires_at=expires_at,
        metadata=metadata or {},
    )


def test_credit_grant_is_expired_false_when_expires_at_is_none(
    now,
):
    grant = make_credit_grant(now=now, expires_at=None)

    assert grant.is_expired(now) is False


def test_credit_grant_is_expired_false_when_expires_at_equals_now(
    now,
):
    grant = make_credit_grant(now=now, expires_at=now)

    assert grant.is_expired(now) is False


def test_credit_grant_is_expired_true_only_when_expires_at_less_than_now(
    now,
):
    grant = make_credit_grant(
        now=now, expires_at=now - timedelta(seconds=1)
    )

    assert grant.is_expired(now) is True


def test_credit_grant_is_depleted_reflects_remaining_credits_is_zero(
    now,
):
    active = make_credit_grant(
        now=now, remaining_credits=Credits(1)
    )
    depleted = make_credit_grant(
        now=now, remaining_credits=Credits(0)
    )

    assert active.is_depleted() is False
    assert depleted.is_depleted() is True


def test_credit_grant_is_active_true_only_when_not_expired_and_not_depleted(
    now,
):
    active = make_credit_grant(
        now=now,
        remaining_credits=Credits(10),
        expires_at=None,
    )
    expired = make_credit_grant(
        now=now,
        remaining_credits=Credits(10),
        expires_at=now - timedelta(seconds=1),
    )
    depleted = make_credit_grant(
        now=now,
        remaining_credits=Credits(0),
        expires_at=None,
    )

    assert active.is_active(now) is True
    assert expired.is_active(now) is False
    assert depleted.is_active(now) is False


def test_credit_grant_consume_reduces_remaining_credits_by_requested_amount(
    now,
):
    grant = make_credit_grant(
        now=now, remaining_credits=Credits(100)
    )

    allocation = grant.consume(Credits(30))

    assert grant.remaining_credits == Credits(70)
    assert allocation.credits == Credits(30)


def test_credit_grant_consume_returns_consumption_allocation_with_same_grant_id(
    now,
):
    grant = make_credit_grant(
        now=now, remaining_credits=Credits(100)
    )

    allocation = grant.consume(Credits(30))

    assert isinstance(allocation, ConsumptionAllocation)
    assert allocation.grant_id == grant.grant_id


def test_credit_grant_consume_raises_invalid_credits_amount_for_zero_consumption(
    now,
):
    grant = make_credit_grant(
        now=now, remaining_credits=Credits(100)
    )

    with pytest.raises(InvalidCreditsAmount):
        grant.consume(Credits(0))


def test_credit_grant_consume_raises_invalid_credits_amount_for_negative_consumption(
    now,
):
    grant = make_credit_grant(
        now=now, remaining_credits=Credits(100)
    )

    with pytest.raises(InvalidCreditsAmount):
        grant.consume(Credits(-1))


def test_credit_grant_consume_raises_invalid_credits_amount_when_amount_exceeds_remaining(
    now,
):
    grant = make_credit_grant(
        now=now, remaining_credits=Credits(10)
    )

    with pytest.raises(InvalidCreditsAmount):
        grant.consume(Credits(11))


def test_credit_consumption_preserves_allocation_tuple_cost_request_id_and_metadata(
    now,
    user_id,
    request_id,
    consumption_id,
):
    allocation = ConsumptionAllocation(
        grant_id=GrantId.new(),
        credits=Credits(25),
    )
    consumption = CreditConsumption(
        consumption_id=consumption_id,
        user_id=user_id,
        cost=Credits(25),
        allocations=(allocation,),
        request_id=request_id,
        created_at=now,
        metadata={"reason": "api_call"},
    )

    assert consumption.allocations == (allocation,)
    assert consumption.cost == Credits(25)
    assert consumption.request_id == request_id
    assert consumption.metadata == {"reason": "api_call"}
