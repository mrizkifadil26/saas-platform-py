# packages/billing/tests/domain/payg/test_events.py

from billing.domain.credits.value_objects import Credits
from billing.domain.payg.events import PaygCreditsGranted
from billing.domain.shared.value_objects import (
    PlanCode,
)


def test_payg_credits_granted_stores_all_fields(
    now, user_id, request_id
):
    event = PaygCreditsGranted(
        user_id=user_id,
        plan_code=PlanCode("starter"),
        request_id=request_id,
        credits=Credits(100),
        occurred_at=now,
        metadata={"source": "checkout"},
    )

    assert event.user_id == user_id
    assert event.plan_code == PlanCode("starter")
    assert event.request_id == request_id
    assert event.credits == Credits(100)
    assert event.occurred_at == now
    assert event.metadata == {"source": "checkout"}


def test_payg_credits_granted_default_metadata_is_none_when_not_explicitly_passed(
    now,
    user_id,
    request_id,
):
    event = PaygCreditsGranted(
        user_id=user_id,
        plan_code=PlanCode("starter"),
        request_id=request_id,
        credits=Credits(100),
        occurred_at=now,
    )

    assert event.metadata == {}
