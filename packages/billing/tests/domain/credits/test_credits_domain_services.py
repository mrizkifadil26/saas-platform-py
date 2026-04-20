from datetime import timedelta

import pytest

from billing.domain.credits.domain_services import (
    consume_credits,
)
from billing.domain.credits.entities import CreditGrant
from billing.domain.credits.exceptions import (
    InsufficientCredits,
    InvalidCreditsAmount,
)
from billing.domain.credits.value_objects import (
    Credits,
    GrantId,
)
from billing.domain.shared.enums import CreditSource
from billing.domain.shared.ids import RequestId, UserId


def make_credit_grant(
    *,
    now,
    grant_id: GrantId,
    user_id: UserId,
    granted_credits: Credits,
    remaining_credits: Credits,
    source: CreditSource,
    expires_at=None,
):
    return CreditGrant(
        grant_id=grant_id,
        user_id=user_id,
        granted_credits=granted_credits,
        remaining_credits=remaining_credits,
        source=source,
        created_at=now,
        expires_at=expires_at,
        metadata={},
    )


def test_consume_credits_rejects_negative_cost(
    now,
    consumption_id,
    user_id,
    request_id,
):
    with pytest.raises(InvalidCreditsAmount):
        consume_credits(
            consumption_id=consumption_id,
            user_id=user_id,
            cost=Credits(-1),
            grants=[],
            request_id=request_id,
            now=now,
        )


def test_consume_credits_allows_zero_cost_and_returns_empty_allocations_no_touched_grants_and_zero_cost_event(
    now,
    consumption_id,
    user_id,
    grant_id,
    request_id,
):
    grant = make_credit_grant(
        grant_id=grant_id,
        now=now,
        user_id=user_id,
        granted_credits=Credits(100),
        remaining_credits=Credits(100),
        source="subscription",
    )

    result = consume_credits(
        consumption_id=consumption_id,
        user_id=user_id,
        cost=Credits(0),
        grants=[grant],
        request_id=request_id,
        now=now,
    )

    assert result.consumption.cost == Credits(0)
    assert result.consumption.allocations == ()
    assert result.touched_grants == ()
    assert result.event.cost == Credits(0)


def test_consume_credits_ignores_grants_belonging_to_other_users(
    now,
    user_id,
    request_id,
    consumption_id,
    grant_id,
):
    foreign = make_credit_grant(
        grant_id=grant_id,
        now=now,
        user_id=UserId("other_user"),
        granted_credits=Credits(100),
        remaining_credits=Credits(100),
        source="subscription",
    )

    with pytest.raises(InsufficientCredits):
        consume_credits(
            consumption_id=consumption_id,
            user_id=user_id,
            cost=Credits(10),
            grants=[foreign],
            request_id=request_id,
            now=now,
        )


def test_consume_credits_ignores_expired_grants(
    now,
    grant_id,
    user_id,
    request_id,
    consumption_id,
):
    expired = make_credit_grant(
        grant_id=grant_id,
        now=now,
        user_id=user_id,
        granted_credits=Credits(100),
        remaining_credits=Credits(100),
        source="subscription",
        expires_at=now - timedelta(seconds=1),
    )

    with pytest.raises(InsufficientCredits):
        consume_credits(
            consumption_id=consumption_id,
            user_id=user_id,
            cost=Credits(10),
            grants=[expired],
            request_id=request_id,
            now=now,
        )


def test_consume_credits_ignores_depleted_grants(
    now,
    user_id,
    grant_id,
    request_id,
    consumption_id,
):
    depleted = make_credit_grant(
        grant_id=grant_id,
        now=now,
        user_id=user_id,
        granted_credits=Credits(100),
        remaining_credits=Credits(0),
        source="subscription",
    )

    with pytest.raises(InsufficientCredits):
        consume_credits(
            consumption_id=consumption_id,
            user_id=user_id,
            cost=Credits(10),
            grants=[depleted],
            request_id=request_id,
            now=now,
        )


def test_consume_credits_raises_insufficient_credits_when_active_credits_are_insufficient(
    now,
    user_id,
    grant_id,
    request_id,
    consumption_id,
):
    grant = make_credit_grant(
        grant_id=grant_id,
        now=now,
        user_id=user_id,
        granted_credits=Credits(100),
        remaining_credits=Credits(5),
        source="subscription",
    )

    with pytest.raises(InsufficientCredits):
        consume_credits(
            consumption_id=consumption_id,
            user_id=user_id,
            cost=Credits(10),
            grants=[grant],
            request_id=RequestId("req_123"),
            now=now,
        )


def test_consume_credits_consumes_from_grants_in_policy_order_not_input_order(
    now,
    user_id,
    request_id,
    consumption_id,
    grant_id,
):
    payg = make_credit_grant(
        grant_id=grant_id,
        now=now,
        user_id=user_id,
        granted_credits=Credits(100),
        remaining_credits=Credits(100),
        source="payg",
    )
    subscription = make_credit_grant(
        grant_id=GrantId.new(),
        now=now,
        user_id=user_id,
        granted_credits=Credits(100),
        remaining_credits=Credits(100),
        source="subscription",
    )

    result = consume_credits(
        consumption_id=consumption_id,
        user_id=user_id,
        cost=Credits(50),
        grants=[payg, subscription],
        request_id=request_id,
        now=now,
    )

    assert (
        result.consumption.allocations[0].grant_id
        == subscription.grant_id
    )


def test_consume_credits_fully_consumes_one_grant_before_moving_to_next(
    now,
    user_id,
    request_id,
    consumption_id,
    grant_id,
):
    first = make_credit_grant(
        grant_id=grant_id,
        now=now,
        user_id=user_id,
        granted_credits=Credits(30),
        remaining_credits=Credits(30),
        source="subscription",
    )
    second = make_credit_grant(
        grant_id=GrantId.new(),
        now=now,
        user_id=user_id,
        granted_credits=Credits(100),
        remaining_credits=Credits(100),
        source="payg",
    )

    result = consume_credits(
        consumption_id=consumption_id,
        user_id=user_id,
        cost=Credits(50),
        grants=[second, first],
        request_id=request_id,
        now=now,
    )

    assert result.touched_grants[
        0
    ].remaining_credits == Credits(0)
    assert result.touched_grants[
        1
    ].remaining_credits == Credits(80)


def test_consume_credits_mutates_only_touched_grants(
    now,
    grant_id,
    user_id,
    request_id,
    consumption_id,
):
    touched = make_credit_grant(
        grant_id=grant_id,
        now=now,
        user_id=user_id,
        granted_credits=Credits(100),
        remaining_credits=Credits(100),
        source="subscription",
    )
    untouched = make_credit_grant(
        grant_id=GrantId.new(),
        now=now,
        user_id=user_id,
        granted_credits=Credits(100),
        remaining_credits=Credits(100),
        source="payg",
    )

    result = consume_credits(
        consumption_id=consumption_id,
        user_id=user_id,
        cost=Credits(30),
        grants=[untouched, touched],
        request_id=request_id,
        now=now,
    )

    changed = {
        grant.grant_id: grant.remaining_credits
        for grant in result.touched_grants
    }
    assert changed[touched.grant_id] == Credits(70)
    assert untouched.grant_id not in changed
    assert untouched.remaining_credits == Credits(100)


def test_consume_credits_returns_credit_consumption_with_expected_allocations(
    now,
    user_id,
    request_id,
    consumption_id,
    grant_id,
):
    first = make_credit_grant(
        grant_id=grant_id,
        now=now,
        user_id=user_id,
        granted_credits=Credits(30),
        remaining_credits=Credits(30),
        source="subscription",
    )
    second = make_credit_grant(
        grant_id=GrantId.new(),
        now=now,
        user_id=user_id,
        granted_credits=Credits(100),
        remaining_credits=Credits(100),
        source="payg",
    )

    result = consume_credits(
        consumption_id=consumption_id,
        user_id=user_id,
        cost=Credits(50),
        grants=[second, first],
        request_id=request_id,
        now=now,
    )

    assert len(result.consumption.allocations) == 2
    assert (
        result.consumption.allocations[0].grant_id
        == first.grant_id
    )
    assert result.consumption.allocations[
        0
    ].credits == Credits(30)
    assert (
        result.consumption.allocations[1].grant_id
        == second.grant_id
    )
    assert result.consumption.allocations[
        1
    ].credits == Credits(20)


def test_consume_credits_returns_credits_consumed_event_mirroring_consumption_data(
    now,
    user_id,
    request_id,
    consumption_id,
    grant_id,
):
    grant = make_credit_grant(
        grant_id=grant_id,
        now=now,
        user_id=user_id,
        granted_credits=Credits(100),
        remaining_credits=Credits(100),
        source="subscription",
    )

    result = consume_credits(
        consumption_id=consumption_id,
        user_id=user_id,
        cost=Credits(10),
        grants=[grant],
        request_id=request_id,
        now=now,
        metadata={"reason": "api_call"},
    )

    assert result.event.user_id == user_id
    assert result.event.request_id == request_id
    assert result.event.cost == Credits(10)
    assert result.event.metadata == {"reason": "api_call"}


def test_consume_credits_copies_metadata_instead_of_reusing_caller_dict(
    now,
    user_id,
    request_id,
    consumption_id,
    grant_id,
):
    grant = make_credit_grant(
        grant_id=grant_id,
        now=now,
        user_id=user_id,
        granted_credits=Credits(100),
        remaining_credits=Credits(100),
        source="subscription",
    )
    metadata = {"reason": "api_call"}

    result = consume_credits(
        consumption_id=consumption_id,
        user_id=user_id,
        cost=Credits(10),
        grants=[grant],
        request_id=request_id,
        now=now,
        metadata=metadata,
    )

    assert result.consumption.metadata == {
        "reason": "api_call"
    }
    assert result.event.metadata == {"reason": "api_call"}
    assert result.consumption.metadata is not metadata
    assert result.event.metadata is not metadata


def test_consume_credits_preserves_request_id_on_consumption_and_event(
    now,
    user_id,
    request_id,
    consumption_id,
    grant_id,
):
    grant = make_credit_grant(
        grant_id=grant_id,
        now=now,
        user_id=user_id,
        granted_credits=Credits(100),
        remaining_credits=Credits(100),
        source="subscription",
    )

    result = consume_credits(
        consumption_id=consumption_id,
        user_id=user_id,
        cost=Credits(10),
        grants=[grant],
        request_id=request_id,
        now=now,
    )

    assert result.consumption.request_id == request_id
    assert result.event.request_id == request_id
