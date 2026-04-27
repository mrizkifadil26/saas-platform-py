from __future__ import annotations

from billing.subscription.domain.subscription_status import SubscriptionStatus
from billing.subscription.infrastructure.persistence.sqlalchemy.mappers.subscription_orm_mapper import (
    SubscriptionORMMapper,
)


def test_subscription_orm_mapper_to_model_and_back(subscription):
    model = SubscriptionORMMapper.to_model(subscription)
    mapped = SubscriptionORMMapper.to_domain(model)

    assert model.subscription_id == str(subscription.subscription_id)
    assert model.user_id == str(subscription.user_id)
    assert model.plan_id == str(subscription.plan_id)
    assert model.metadata_json is None
    assert len(model.items) == 1
    assert mapped.subscription_id == subscription.subscription_id
    assert mapped.user_id == subscription.user_id
    assert mapped.plan_id == subscription.plan_id
    assert mapped.status == SubscriptionStatus.ACTIVE
    assert mapped.items == subscription.items


def test_subscription_orm_mapper_update_model_replaces_mutable_fields(
    make_subscription,
    subscription,
):
    model = SubscriptionORMMapper.to_model(subscription)
    updated_subscription = make_subscription(
        subscription_id=subscription.subscription_id,
        status=SubscriptionStatus.PAST_DUE,
        items=(),
        cancel_at_period_end=True,
        metadata={"source": "updated"},
    )

    updated_model = SubscriptionORMMapper.update_model(model, updated_subscription)

    assert updated_model.status == SubscriptionStatus.PAST_DUE.value
    assert updated_model.cancel_at_period_end is True
    assert updated_model.metadata_json == '{"source": "updated"}'
    assert updated_model.items == []
