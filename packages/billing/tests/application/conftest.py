from datetime import datetime, timedelta

import pytest

from billing.application.subscription.interfaces import (
    CreditGrantWriter,
    EventPublisher,
    IdempotencyStore,
    SubscriptionApplicationUnitOfWork,
)
from billing.domain.shared.ids import UserId
from billing.domain.shared.value_objects import PlanCode
from billing.domain.subscription.entities import (
    Subscription,
)
from billing.domain.subscription.value_objects import (
    SubscriptionId,
)


class FakeSubscriptionRepository:
    def __init__(self) -> None:
        self.by_id: dict[str, Subscription] = {}

    async def get(
        self,
        subscription_id: SubscriptionId,
    ) -> Subscription | None:
        return self.by_id.get(str(subscription_id))

    async def get_active_for_user(
        self,
        user_id: UserId,
    ) -> Subscription | None:
        for subscription in self.by_id.values():
            if str(subscription.user_id) == str(
                user_id
            ) and subscription.status in (
                "active",
                "past_due",
            ):
                return subscription

        return None

    async def save(
        self,
        subscription: Subscription,
    ) -> None:
        self.by_id[str(subscription.subscription_id)] = (
            subscription
        )


class FakeCreditGrantRepository(CreditGrantWriter):
    def __init__(self) -> None:
        self.items: list[object] = []

    async def save(self, grant: object) -> None:
        self.items.append(grant)


class FakeEventPublisher(EventPublisher):
    def __init__(self) -> None:
        self.events: list[object] = []

    def publish(self, event: object) -> None:
        self.events.append(event)


class FakeIdempotencyStore(IdempotencyStore):
    def __init__(self) -> None:
        self.data: dict[str, str] = {}

    def get(self, key: str) -> str | None:
        return self.data.get(key)

    def save(self, key: str, fingerprint: str) -> None:
        self.data[key] = fingerprint


class FakeUnitOfWork(SubscriptionApplicationUnitOfWork):
    subscription: FakeSubscriptionRepository
    credit_grant: FakeCreditGrantRepository

    def __init__(self) -> None:
        self.subscription = FakeSubscriptionRepository()
        self.credit_grant = FakeCreditGrantRepository()
        self.committed = False
        self.rollback_called = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rollback_called = True


@pytest.fixture
def active_subscription(
    user_id: UserId,
    plan_code: PlanCode,
    now: datetime,
) -> Subscription:
    return Subscription(
        subscription_id=SubscriptionId.new(),
        user_id=user_id,
        plan_code=plan_code,
        status="active",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
        cancel_at_period_end=False,
        provider_subscription_id="prov_sub_123",
        last_granted_period_start=None,
    )


@pytest.fixture
def past_due_subscription(
    user_id: UserId,
    plan_code: PlanCode,
    now: datetime,
) -> Subscription:
    return Subscription(
        subscription_id=SubscriptionId.new(),
        user_id=user_id,
        plan_code=plan_code,
        status="past_due",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
        cancel_at_period_end=False,
        provider_subscription_id="prov_sub_123",
        last_granted_period_start=None,
    )


@pytest.fixture
def canceled_subscription(
    user_id: UserId,
    plan_code: PlanCode,
    now: datetime,
) -> Subscription:
    return Subscription(
        subscription_id=SubscriptionId.new(),
        user_id=user_id,
        plan_code=plan_code,
        status="canceled",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
        cancel_at_period_end=True,
        provider_subscription_id="prov_sub_123",
        last_granted_period_start=None,
    )


@pytest.fixture
def uow() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def event_publisher() -> FakeEventPublisher:
    return FakeEventPublisher()


@pytest.fixture
def idempotency_store() -> FakeIdempotencyStore:
    return FakeIdempotencyStore()
