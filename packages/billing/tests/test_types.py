from billing.domain.types import Credits, PlanCode, RequestId


def test_credits_wraps_int():
    value = Credits(100)
    assert value == 100
    assert isinstance(value, int)


def test_plan_code_wraps_str():
    value = PlanCode("sub_basic_monthly")
    assert value == "sub_basic_monthly"
    assert isinstance(value, str)


def test_request_id_wraps_str():
    value = RequestId("req_123")
    assert value == "req_123"
    assert isinstance(value, str)
