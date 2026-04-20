# packages/billing/tests/domain/payg/test_value_objects.py

from billing.domain.payg.value_objects import PaygPurchaseId


def test_payg_purchase_id_new_returns_uuid_backed_id():
    value = PaygPurchaseId.new()

    assert isinstance(value, PaygPurchaseId)
    assert str(value)
    assert len(str(value)) == 36


def test_payg_purchase_id_str_returns_uuid_string():
    value = PaygPurchaseId.new()

    assert str(value) == str(value.value)
