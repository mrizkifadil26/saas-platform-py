# packages/billing/tests/domain/shared/test_ids.py

import pytest
from billing.domain.shared.ids import RequestId, UserId


def test_request_id_trims_surrounding_whitespace():
    value = RequestId("  req_123  ")

    assert value.value == "req_123"


def test_request_id_rejects_empty_string():
    with pytest.raises(ValueError, match="RequestId"):
        RequestId("   ")


def test_request_id_str_returns_normalized_value():
    value = RequestId("  req_123  ")

    assert str(value) == "req_123"


def test_user_id_str_returns_underlying_value():
    value = UserId("user_123")

    assert str(value) == "user_123"
