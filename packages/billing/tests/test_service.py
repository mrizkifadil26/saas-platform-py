import pytest
from billing.charge import consume_credits
from billing.errors import IdempotencyConflict, InsufficientCredits
from billing.models import Wallet
from billing.types import Credits, RequestId, UserId


def test_consume_credits_success():
    wallet = Wallet(
        user_id=UserId("user_123"),
        credits=Credits(100),
    )

    result = consume_credits(
        wallet=wallet,
        cost=Credits(40),
        request_id=RequestId("req_123"),
        used_request_ids=set(),
    )

    assert result.wallet.user_id == UserId("user_123")
    assert result.wallet.credits == Credits(60)

    assert result.event.event_type == "credits_charged"
    assert result.event.user_id == UserId("user_123")
    assert result.event.credits == Credits(40)
    assert result.event.request_id == RequestId("req_123")
    assert result.event.plan_code is None


def test_consume_credits_insufficient():
    wallet = Wallet(
        user_id=UserId("user_123"),
        credits=Credits(10),
    )

    with pytest.raises(InsufficientCredits):
        consume_credits(
            wallet=wallet,
            cost=Credits(40),
            request_id=RequestId("req_123"),
            used_request_ids=set(),
        )


def test_consume_credits_idempotency_conflict():
    wallet = Wallet(
        user_id=UserId("user_123"),
        credits=Credits(100),
    )

    with pytest.raises(IdempotencyConflict):
        consume_credits(
            wallet=wallet,
            cost=Credits(40),
            request_id=RequestId("req_123"),
            used_request_ids={"req_123"},
        )
