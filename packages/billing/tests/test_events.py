from billing.domain.events import BillingEvent
from billing.domain.types import Credits, PlanCode, RequestId, UserId


def test_billing_event_fields():
    event = BillingEvent(
        event_type="payg_credits_granted",
        user_id=UserId("user_123"),
        credits=Credits(100),
        plan_code=PlanCode("payg_10_usd"),
        request_id=RequestId("req_456"),
    )

    assert event.event_type == "payg_credits_granted"
    assert event.user_id == UserId("user_123")
    assert event.credits == Credits(100)
    assert event.plan_code == PlanCode("payg_10_usd")
    assert event.request_id == RequestId("req_456")
