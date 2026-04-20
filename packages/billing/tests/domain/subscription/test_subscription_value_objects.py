from uuid import UUID

from billing.domain.subscription.value_objects import (
    SubscriptionId,
)


def test_subscription_id_new_returns_uuid_backed_id():
    value = SubscriptionId.new()

    assert isinstance(value, SubscriptionId)
    assert isinstance(value.value, UUID)
    assert len(str(value.value)) == 36  # UUID string length


def test_subscription_id_str_returns_uuid_string():
    value = SubscriptionId.new()

    assert str(value) == str(value.value)
