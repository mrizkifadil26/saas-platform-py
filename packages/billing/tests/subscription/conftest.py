from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
from uuid import uuid4

import pytest

from billing.shared.application.clock import Clock
from billing.shared.application.event_publisher import EventPublisher
from billing.shared.application.id_generator import IdGenerator
from billing.shared.application.uow import BillingUoW
from billing.shared.domain.value_objects.user_id import UserId
from billing.subscription.domain.subscription import Subscription
from billing.subscription.domain.subscription_item import SubscriptionItem
from billing.subscription.domain.subscription_repository import SubscriptionRepository
from billing.subscription.domain.subscription_status import SubscriptionStatus
from billing.subscription.domain.value_objects.billing_period import BillingPeriod
from billing.subscription.domain.value_objects.feature_code import FeatureCode
from billing.subscription.domain.value_objects.plan_id import PlanId
from billing.subscription.domain.value_objects.product_code import ProductCode
from billing.subscription.domain.value_objects.subscription_id import SubscriptionId
from billing.subscription.domain.value_objects.subscription_item_id import (
    SubscriptionItemId,
)


def uuid_str() -> str:
    return str(uuid4())


@pytest.fixture
def user_id() -> UserId:
    return UserId(uuid_str())


@pytest.fixture
def plan_id() -> PlanId:
    return PlanId(uuid_str())


@pytest.fixture
def new_plan_id() -> PlanId:
    return PlanId(uuid_str())


@pytest.fixture
def subscription_id() -> SubscriptionId:
    return SubscriptionId(uuid_str())


@pytest.fixture
def item_id() -> SubscriptionItemId:
    return SubscriptionItemId(uuid_str())


@pytest.fixture
def product_code() -> ProductCode:
    return ProductCode(uuid_str())


@pytest.fixture
def feature_code() -> FeatureCode:
    return FeatureCode(uuid_str())


@pytest.fixture
def billing_period(now) -> BillingPeriod:
    return BillingPeriod(
        start_at=now,
        end_at=now + timedelta(days=30),
    )


@pytest.fixture
def next_billing_period(billing_period: BillingPeriod) -> BillingPeriod:
    return BillingPeriod(
        start_at=billing_period.end_at,
        end_at=billing_period.end_at + timedelta(days=30),
    )


@pytest.fixture
def subscription_item(
    item_id: SubscriptionItemId,
    product_code: ProductCode,
    feature_code: FeatureCode,
) -> SubscriptionItem:
    return SubscriptionItem(
        item_id=item_id,
        product_code=product_code,
        feature_code=feature_code,
        quantity=2,
    )


@pytest.fixture
def make_subscription(
    user_id: UserId,
    plan_id: PlanId,
    billing_period: BillingPeriod,
) -> Callable[..., Subscription]:
    def factory(
        *,
        subscription_id: SubscriptionId | None = None,
        status: SubscriptionStatus = SubscriptionStatus.ACTIVE,
        current_period: BillingPeriod | None = None,
        items: tuple[SubscriptionItem, ...] = (),
        cancel_at_period_end: bool = False,
        provider_subscription_id: str | None = "prov_sub_123",
        last_granted_period_start=None,
        metadata: dict | None = None,
    ) -> Subscription:
        return Subscription(
            subscription_id=subscription_id or SubscriptionId(uuid_str()),
            user_id=user_id,
            plan_id=plan_id,
            status=status,
            billing_period=current_period or billing_period,
            items=items,
            cancel_at_period_end=cancel_at_period_end,
            provider_subscription_id=provider_subscription_id,
            last_granted_period_start=last_granted_period_start,
            metadata=metadata or {},
        )

    return factory


@pytest.fixture
def subscription(
    make_subscription: Callable[..., Subscription],
    subscription_item: SubscriptionItem,
) -> Subscription:
    return make_subscription(items=(subscription_item,))


class FakeSubscriptionRepository(SubscriptionRepository):
    def __init__(self) -> None:
        self.items: dict[str, Subscription] = {}
        self.saved: list[Subscription] = []
        self.deleted: list[Subscription] = []

    async def get(self, entity_id: SubscriptionId) -> Subscription | None:
        return self.items.get(str(entity_id))

    async def save(self, entity: Subscription) -> None:
        self.items[str(entity.subscription_id)] = entity
        self.saved.append(entity)

    async def delete(self, entity: Subscription) -> None:
        self.items.pop(str(entity.subscription_id), None)
        self.deleted.append(entity)

    async def find_active_by_user(self, user_id: UserId) -> Subscription | None:
        for subscription in self.items.values():
            if subscription.user_id == user_id and subscription.status.is_activeish:
                return subscription
        return None

    async def find_due_for_renewal(self, now) -> list[Subscription]:
        return [
            s
            for s in self.items.values()
            if s.can_renew() and not s.cancel_at_period_end and s.current_period_end <= now
        ]

    async def find_canceling_subscriptions(self) -> list[Subscription]:
        return [s for s in self.items.values() if s.cancel_at_period_end]


class FakeEventPublisher(EventPublisher):
    def __init__(self) -> None:
        self.published_batches: list[list[object]] = []

    def publish(self, events) -> None:
        self.published_batches.append(list(events))


class FakeClock(Clock):
    def __init__(self, current_time) -> None:
        self._current_time = current_time

    def now(self):
        return self._current_time


class FakeIdGenerator(IdGenerator):
    def __init__(self, value: str) -> None:
        self._value = value

    def generate(self) -> str:
        return self._value


class FakeSubscriptionUoW(BillingUoW):
    def __init__(self, repository: FakeSubscriptionRepository) -> None:
        self._subscriptions = repository
        self.commit_count = 0
        self.rollback_count = 0

    @property
    def subscriptions(self) -> SubscriptionRepository:
        return self._subscriptions

    async def commit(self) -> None:
        self.commit_count += 1

    async def rollback(self) -> None:
        self.rollback_count += 1


@pytest.fixture
def subscription_repository() -> FakeSubscriptionRepository:
    return FakeSubscriptionRepository()


@pytest.fixture
def event_publisher() -> FakeEventPublisher:
    return FakeEventPublisher()


@pytest.fixture
def clock(now) -> FakeClock:
    return FakeClock(now)


@pytest.fixture
def id_generator() -> FakeIdGenerator:
    return FakeIdGenerator(uuid_str())


@pytest.fixture
def subscription_uow(
    subscription_repository: FakeSubscriptionRepository,
) -> FakeSubscriptionUoW:
    return FakeSubscriptionUoW(subscription_repository)
