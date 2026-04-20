# packages/billing/tests/domain/credits/test_events.py

from billing.domain.credits.events import CreditsConsumed
from billing.domain.credits.value_objects import (
    ConsumptionId,
    Credits,
)


def test_credits_consumed_stores_all_passed_fields(
    now,
    user_id,
    request_id,
):
    event = CreditsConsumed(
        consumption_id=ConsumptionId.new(),
        user_id=user_id,
        request_id=request_id,
        allocations=(),
        cost=Credits(25),
        occurred_at=now,
        metadata={"reason": "api_call"},
    )

    assert event.user_id == user_id
    assert event.request_id == request_id
    assert event.cost == Credits(25)
    assert event.occurred_at == now
    assert event.metadata == {"reason": "api_call"}


def test_credits_consumed_default_metadata_is_empty_dict(
    now,
    user_id,
    request_id,
):
    event = CreditsConsumed(
        consumption_id=ConsumptionId.new(),
        user_id=user_id,
        request_id=request_id,
        allocations=(),
        cost=Credits(25),
        occurred_at=now,
    )

    assert event.metadata == {}
