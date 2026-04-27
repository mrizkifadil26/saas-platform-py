from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

import pytest

from billing.shared.domain.value_objects.user_id import UserId
from billing.shared.infrastructure.persistence.sqlalchemy.uow import (
    SQLAlchemyBillingUoW,
)
from billing.subscription.infrastructure.persistence.sqlalchemy.models.subscription_model import (
    SubscriptionModel,
)
from billing.subscription.infrastructure.persistence.sqlalchemy.repositories.sql_subscription_repository import (
    SQLSubscriptionRepository,
)


@dataclass
class FakeScalarResult:
    one: object | None = None
    many: list[object] | None = None

    def scalar_one_or_none(self):
        return self.one

    def scalars(self):
        return self

    def all(self):
        return list(self.many or [])


class FakeAsyncSession:
    def __init__(self) -> None:
        self.models: dict[str, SubscriptionModel] = {}
        self.deleted: list[SubscriptionModel] = []
        self.execute_results: list[FakeScalarResult] = []
        self.commit_count = 0
        self.rollback_count = 0
        self.close_count = 0

    async def get(self, model_type, key):
        return self.models.get(key)

    def add(self, model):
        self.models[model.subscription_id] = model

    async def delete(self, model):
        self.deleted.append(model)
        self.models.pop(model.subscription_id, None)

    async def execute(self, stmt):
        return self.execute_results.pop(0)

    async def commit(self):
        self.commit_count += 1

    async def rollback(self):
        self.rollback_count += 1

    async def close(self):
        self.close_count += 1


@pytest.mark.asyncio
async def test_sql_subscription_repository_save_and_get(subscription):
    session = FakeAsyncSession()
    repository = SQLSubscriptionRepository(session)

    await repository.save(subscription)

    found = await repository.get(subscription.subscription_id)

    assert found is not None
    assert found.subscription_id == subscription.subscription_id
    assert found.items == subscription.items


@pytest.mark.asyncio
async def test_sql_subscription_repository_updates_existing_subscription(subscription):
    session = FakeAsyncSession()
    repository = SQLSubscriptionRepository(session)
    await repository.save(subscription)

    updated = subscription.cancel(immediate=False)
    await repository.save(updated)

    found = await repository.get(subscription.subscription_id)

    assert found is not None
    assert found.cancel_at_period_end is True


@pytest.mark.asyncio
async def test_sql_subscription_repository_queries_active_due_and_canceling_sets(
    make_subscription,
    user_id,
):
    session = FakeAsyncSession()
    repository = SQLSubscriptionRepository(session)
    active = make_subscription()
    canceling = make_subscription(cancel_at_period_end=True)
    due = make_subscription()
    other_user = make_subscription()
    object.__setattr__(other_user, "user_id", UserId(str(uuid4())))
    session.execute_results = [
        FakeScalarResult(one=repository._to_model(active)),
        FakeScalarResult(
            many=[
                repository._to_model(active),
                repository._to_model(due),
            ]
        ),
        FakeScalarResult(
            many=[
                repository._to_model(canceling),
            ]
        ),
    ]

    found_active = await repository.find_active_by_user(user_id)
    due_items = await repository.find_due_for_renewal(due.current_period_end)
    canceling_items = await repository.find_canceling_subscriptions()

    assert found_active is not None
    assert found_active.user_id == user_id
    assert active.subscription_id in {item.subscription_id for item in due_items}
    assert due.subscription_id in {item.subscription_id for item in due_items}
    assert canceling.subscription_id in {
        item.subscription_id for item in canceling_items
    }


@pytest.mark.asyncio
async def test_subscription_uow_exposes_repository_and_transaction_boundaries(
    subscription,
):
    session = FakeAsyncSession()

    def session_factory():
        return session

    uow = SQLAlchemyBillingUoW(session_factory)

    with pytest.raises(RuntimeError, match="not been entered"):
        _ = uow.subscriptions

    async with uow:
        await uow.subscriptions.save(subscription)

    async with uow:
        found = await uow.subscriptions.get(subscription.subscription_id)

    assert found is not None
    assert found.subscription_id == subscription.subscription_id
    assert session.commit_count == 2
    assert session.close_count == 2
