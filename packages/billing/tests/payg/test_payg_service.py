import pytest
from billing.errors import IdempotencyConflict
from billing.models import Wallet
from billing.payg.service import grant_payg_credits
from billing.types import Credits, PlanCode, RequestId, UserId


def test_grant_payg_credits_success():
    wallet = Wallet(
        user_id=UserId("user_123"),
        credits=Credits(100),
    )
    used_ids = set()

    result = grant_payg_credits(
        wallet=wallet,
        plan_code=PlanCode("payg_10_usd"),
        request_id=RequestId("req_123"),
        used_request_ids=used_ids,
    )

    assert result.wallet.user_id == UserId("user_123")
    assert result.wallet.credits == Credits(200)

    assert result.plan.code == PlanCode("payg_10_usd")
    assert result.plan.credits_grant == Credits(100)

    assert result.event.event_type == "payg_credits_granted"
    assert result.event.user_id == UserId("user_123")
    assert result.event.credits == Credits(100)
    assert result.event.plan_code == PlanCode("payg_10_usd")
    assert result.event.request_id == RequestId("req_123")

    assert used_ids == {"req_123"}


def test_grant_payg_credits_idempotency_conflict():
    wallet = Wallet(
        user_id=UserId("user_123"),
        credits=Credits(100),
    )
    used_ids = {"req_123"}

    with pytest.raises(IdempotencyConflict):
        grant_payg_credits(
            wallet=wallet,
            plan_code=PlanCode("payg_10_usd"),
            request_id=RequestId("req_123"),
            used_request_ids=used_ids,
        )
