from datetime import timedelta

from billing.application.subscription.commands import (
    CreateSubscriptionCommand,
)
from billing.application.subscription.services import (
    SubscriptionApplicationService,
)
from billing.domain.subscription.events import (
    SubscriptionCreated,
)


def test_create_subscription_success(
    uow,
    event_publisher,
    idempotency_store,
    user_id,
    plan_code,
    now,
):
    service = SubscriptionApplicationService(
        uow=uow,
        event_publisher=event_publisher,
        idempotency_store=idempotency_store,
    )

    result = service.create_subscription(
        CreateSubscriptionCommand(
            user_id=user_id,
            plan_code=plan_code,
            current_period_start=now,
            current_period_end=now + timedelta(days=30),
            provider_subscription_id="prov_sub_123",
            now=now,
        )
    )

    assert result.user_id == str(user_id)
    assert result.plan_code == str(plan_code)
    assert result.status == "active"
    assert result.cancel_at_period_end is False
    assert result.provider_subscription_id == "prov_sub_123"
    assert result.subscription_id in uow.subscriptions.by_id

    assert uow.committed is True
    assert len(event_publisher.events) == 1
    assert isinstance(
        event_publisher.events[0], SubscriptionCreated
    )
