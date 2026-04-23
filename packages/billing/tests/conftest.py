from datetime import datetime, timezone
from uuid import uuid4

import pytest
from billing.domain.credits.value_objects import (
    ConsumptionId,
    GrantId,
)
from billing.domain.shared.ids import RequestId, UserId
from billing.domain.shared.value_objects import PlanCode
from billing.domain.subscription.value_objects import (
    SubscriptionId,
)

UTC = timezone.utc


def dt(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
) -> datetime:
    return datetime(
        year, month, day, hour, minute, second, tzinfo=UTC
    )


@pytest.fixture
def now() -> datetime:
    return dt(2026, 4, 20, 12, 0, 0)


@pytest.fixture
def user_id() -> UserId:
    return UserId("user_123")


@pytest.fixture
def subscription_id() -> SubscriptionId:
    return SubscriptionId.new()


@pytest.fixture
def grant_id() -> GrantId:
    return GrantId.new()


@pytest.fixture
def consumption_id() -> ConsumptionId:
    return ConsumptionId.new()


@pytest.fixture
def request_id() -> RequestId:
    return RequestId(f"req_{uuid4().hex}")


@pytest.fixture
def plan_code() -> PlanCode:
    return PlanCode("sub_basic_monthly")
