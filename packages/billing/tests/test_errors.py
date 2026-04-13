from billing.domain.errors import BillingError, IdempotencyConflict, InsufficientCredits, UnknownPlan


def test_insufficient_credits_is_billing_error():
    err = InsufficientCredits("not enough")
    assert isinstance(err, BillingError)
    assert str(err) == "not enough"


def test_unknown_plan_is_billing_error():
    err = UnknownPlan("bad plan")
    assert isinstance(err, BillingError)
    assert str(err) == "bad plan"


def test_idempotency_conflict_is_billing_error():
    err = IdempotencyConflict("duplicate")
    assert isinstance(err, BillingError)
    assert str(err) == "duplicate"
