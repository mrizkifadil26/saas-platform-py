# packages/billing/tests/domain/payg/test_entities.py

from billing.domain.credits.value_objects import Credits
from billing.domain.payg.entities import PaygPurchase
from billing.domain.payg.value_objects import PaygPurchaseId
from billing.domain.shared.value_objects import (
    PlanCode,
)


def test_payg_purchase_preserves_passed_fields(
    now,
    user_id,
    request_id,
):
    purchase = PaygPurchase(
        purchase_id=PaygPurchaseId.new(),
        user_id=user_id,
        plan_code=PlanCode("payg_10_usd"),
        credits=Credits(100),
        request_id=request_id,
        created_at=now,
        metadata={"source": "checkout"},
    )

    assert purchase.purchase_id
    assert purchase.user_id == user_id
    assert purchase.plan_code == PlanCode("payg_10_usd")
    assert purchase.request_id == request_id
    assert purchase.created_at == now
    assert purchase.metadata == {"source": "checkout"}


def test_payg_purchase_default_metadata_is_empty_dict(
    now,
    user_id,
    request_id,
):
    purchase = PaygPurchase(
        purchase_id=PaygPurchaseId.new(),
        user_id=user_id,
        plan_code=PlanCode("payg_10_usd"),
        credits=Credits(100),
        request_id=request_id,
        created_at=now,
    )

    assert purchase.metadata == {}
